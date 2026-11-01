"""Business operations for inventory lots."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import Item, Lot, LotKind, SessionLine, SessionLineType
from api.db.repositories import LotRepository

from .item_service import ItemService, get_item_service
from .session_line_service import SessionLineService, get_session_line_service


class LotService:
    """Provide lot creation and FIFO inventory use cases."""

    def __init__(
        self,
        session: AsyncSession,
        repository: LotRepository,
        item_service: ItemService,
        session_line_service: SessionLineService,
    ) -> None:
        self._session = session
        self._repository = repository
        self._item_service = item_service
        self._session_line_service = session_line_service

    async def create_lot(
        self,
        *,
        user_id: UUID,
        kind: LotKind,
        session_line_id: UUID,
        quantity: int,
        tt: Decimal | None,
    ) -> Lot:
        """Create a lot for an owned produced session line.

        The connected user's identifier is the lot owner. The session-line
        service verifies that the line belongs to the same user.
        """

        async with self._session.begin():
            session_line = await self._session_line_service.get_session_line_for_user(
                session_line_id=session_line_id,
                user_id=user_id,
            )
            if session_line is None:
                raise AppError(404, "Session line not found")
            if session_line.type is not SessionLineType.PRODUCED:
                raise UnprocessingError("Only produced session lines can create lots")

            if kind is LotKind.TOOL and quantity != 1:
                raise UnprocessingError("Tool quantity must be 1")
            if kind is LotKind.TOOL and tt is None:
                raise UnprocessingError("tt is required for tools")
            return await self._repository.create(
                user_id=user_id,
                session_line=session_line,
                kind=kind.value,
                quantity=quantity,
                tt=tt if kind is LotKind.TOOL else None,
            )

    async def get_fifo_lots(
        self, *, user_id: UUID, item_id: UUID
    ) -> tuple[Item, list[Lot], int]:
        """Return an item, its usable FIFO lots, and their total quantity.

        The repository enforces ownership, active status, positive quantity,
        and FIFO ordering. Non-stackable items raise HTTP 409.
        """

        stackable = await self._item_service.is_item_stackable(item_id=item_id)
        if stackable is False:
            raise UnprocessingError("Item is not stackable")
        if stackable is None:
            raise AppError(404, "Item not found")
        item, lots, total_quantity = await self._repository.get_fifo_lots_for_item(
            user_id=user_id,
            item_id=item_id,
        )
        if item is None:
            raise AppError(404, "Item not found")
        return item, lots, total_quantity

    async def allocate_fifo_quantity(
        self, *, lots: list[Lot], quantity: int
    ) -> list[tuple[Lot, int]]:
        """Allocate a quantity across already locked lots in FIFO order."""

        if quantity < 1:
            raise UnprocessingError("Quantity must be at least 1")

        remaining = quantity
        allocations: list[tuple[Lot, int]] = []
        for lot in lots:
            available_quantity = lot.qty - lot.reserved
            allocated_quantity = min(remaining, available_quantity)
            if allocated_quantity <= 0:
                continue
            allocations.append((lot, allocated_quantity))
            remaining -= allocated_quantity
            if remaining == 0:
                break

        if remaining != 0:
            raise UnprocessingError("Unable to allocate the requested quantity")
        return allocations

    async def get_unstackable_lot(self, *, user_id: UUID, lot_id: UUID) -> Lot:
        """Return an owned unstackable lot with its item-specific details."""

        lot = await self._repository.get_unstackable_lot(
            user_id=user_id,
            lot_id=lot_id,
        )
        if lot is None:
            raise AppError(404, "Lot not found")
        if lot.origin is None or lot.origin.item is None:
            raise AppError(404, "Item not found")
        stackable = await self._item_service.is_item_stackable(
            item_id=lot.origin.item.id
        )
        if stackable is True:
            raise UnprocessingError("Only unstackable items have lots")
        if stackable is None:
            raise AppError(404, "Item not found")
        if lot.tool_lot is None:
            raise UnprocessingError("Lot is not an unstackable tool lot")
        return lot

    async def create_transaction_lot(
        self,
        *,
        user_id: UUID,
        session_line: SessionLine,
        kind: LotKind,
        quantity: int,
        tt: Decimal | None,
    ) -> Lot:
        """Create the lot produced by a BUY session line in its open transaction."""

        if kind is LotKind.TOOL and quantity != 1:
            raise UnprocessingError("Tool quantity must be 1")
        if kind is LotKind.TOOL and tt is None:
            raise UnprocessingError("tt is required for tools")
        return await self._repository.create(
            user_id=user_id,
            session_line=session_line,
            kind=kind.value,
            quantity=quantity,
            tt=tt if kind is LotKind.TOOL else None,
        )


    async def _get_stackable_lot(
        self, *, user_id: UUID, lot_id: UUID
    ) -> Lot:
        """Load an owned lot and verify that its item is stackable."""

        lot = await self._repository.get_origin_with_item(
            user_id=user_id,
            lot_id=lot_id,
        )
        if lot is None:
            raise AppError(404, "Lot not found")
        if lot.origin is None or lot.origin.item is None:
            raise AppError(404, "Item not found")

        stackable = await self._item_service.is_item_stackable(
            item_id=lot.origin.item.id
        )
        if stackable is False:
            raise UnprocessingError("Item is not stackable")
        if stackable is None:
            raise AppError(404, "Item not found")
        return lot

    async def reserve_quantity(
        self, *, user_id: UUID, lot_id: UUID, quantity: int
    ) -> Lot:
        """Reserve available quantity from an owned stackable lot.

        ``qty`` is unchanged and ``reserved`` increases by ``quantity``.
        Quantity cannot exceed the currently available stock. A zero quantity
        is a no-op and returns the lot without updating it.
        """

        if quantity < 0:
            raise UnprocessingError("Reservation quantity cannot be negative")

        async with self._session.begin():
            lot = await self._get_stackable_lot(
                user_id=user_id,
                lot_id=lot_id,
            )
            if quantity == 0:
                return lot
            available_quantity = lot.qty - lot.reserved
            if available_quantity < quantity:
                raise UnprocessingError("Insufficient quantity available to reserve")

            return await self._repository.update_quantities(
                lot=lot,
                quantity=lot.qty,
                reserved=lot.reserved + quantity,
                is_active=lot.is_active,
            )

    async def reserve_for_sale(
        self, *, lots: list[tuple[Lot, int]]
    ) -> None:
        """Reserve sale quantities without changing lot stock.

        The caller must already own the surrounding database transaction and
        provide lots locked for update. Each reservation increases ``reserved``
        while preserving ``qty`` and ``is_active``.
        """

        for lot, quantity in lots:
            if quantity < 1:
                raise UnprocessingError("Reservation quantity must be positive")
            if lot.qty - lot.reserved < quantity:
                raise UnprocessingError("Insufficient quantity available to reserve")
            
            await self._repository.update_quantities(
                lot=lot,
                quantity=lot.qty,
                reserved=lot.reserved + quantity,
                is_active=lot.is_active,
            )

    async def reserve_unstackable_for_sale(self, *, lot: Lot) -> None:
        """Reserve one unstackable lot without consuming its stock quantity."""

        if lot.qty != 1 or lot.reserved != 0:
            raise UnprocessingError("Unstackable lot is not available to reserve")
        
        await self._repository.update_quantities(
            lot=lot,
            quantity=lot.qty,
            reserved=1,
            is_active=lot.is_active,
        )

    async def consume_for_consumption(
        self, *, lots: list[tuple[Lot, int]]
    ) -> None:
        """Consume available material quantities from locked FIFO lots."""

        for lot, quantity in lots:
            if quantity < 1:
                raise UnprocessingError("Consumption quantity must be positive")
            if lot.qty - lot.reserved < quantity:
                raise UnprocessingError("Insufficient quantity available to consume")
            remaining_quantity = lot.qty - quantity
            await self._repository.update_quantities(
                lot=lot,
                quantity=remaining_quantity,
                reserved=lot.reserved,
                is_active=remaining_quantity > 0,
            )

    async def get_lot_by_id(
        self, *, user_id: UUID, lot_id: UUID
    ) -> Lot:
        """Load an owned lot by ID with a row lock for settlement."""

        lot = await self._repository.get_origin_with_item(
            user_id=user_id, lot_id=lot_id
        )
        if lot is None:
            raise AppError(404, "Lot not found")
        return lot

    async def settle_sale_lot(
        self, *, lot: Lot, quantity: int, sold: bool
    ) -> None:
        """Settle or release a sale reservation on one locked lot.

        SOLD reduces ``qty`` by the reserved line quantity. RETURNED and
        CANCELLED leave ``qty`` untouched. All transitions release only this
        transaction's reservation so concurrent reservations remain intact.
        """

        if quantity < 1 or lot.reserved < quantity:
            raise UnprocessingError("Lot reservation is no longer available")
        remaining_quantity = lot.qty - quantity if sold else lot.qty
        await self._repository.update_quantities(
            lot=lot,
            quantity=remaining_quantity,
            reserved=lot.reserved - quantity,
            is_active=lot.is_active if not sold else remaining_quantity > 0,
        )

    async def consume_reserved_quantity(
        self, *, user_id: UUID, lot_id: UUID, quantity: int
    ) -> Lot:
        """Consume reserved quantity from an owned stackable lot.

        Both ``qty`` and ``reserved`` decrease by ``quantity``. The requested
        quantity cannot exceed the lot's reservation. A zero quantity is a
        no-op and returns the lot without updating it.
        """

        if quantity < 0:
            raise UnprocessingError("Consumption quantity cannot be negative")

        async with self._session.begin():
            lot = await self._get_stackable_lot(
                user_id=user_id,
                lot_id=lot_id,
            )
            if quantity == 0:
                return lot
            if lot.reserved < quantity:
                raise UnprocessingError("Insufficient reserved quantity")

            remaining_quantity = lot.qty - quantity
            remaining_reserved = lot.reserved - quantity
            return await self._repository.update_quantities(
                lot=lot,
                quantity=remaining_quantity,
                reserved=remaining_reserved,
                is_active=not (remaining_quantity == 0 and remaining_reserved == 0),
            )


def get_lot_service(session: AsyncSession) -> LotService:
    """Build a lot service with its domain service dependencies."""

    return LotService(
        session=session,
        repository=LotRepository(session),
        item_service=get_item_service(session),
        session_line_service=get_session_line_service(session),
    )
