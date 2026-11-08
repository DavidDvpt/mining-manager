"""Business operations for named transaction sessions."""

from contextlib import asynccontextmanager
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import (
    LotKind,
    Session,
    SessionTransaction,
    SessionTransactionStatus,
    SessionTransactionType,
    SessionTransactionTypeDetail,
)
from api.db.repositories import SessionTransactionRepository
from api.db.repositories.material_repository import MaterialRepository

from .item_service import ItemService, get_item_service, is_limited_item
from .lot_service import LotService, get_lot_service
from .material_service import MaterialService


@asynccontextmanager
async def _transaction_scope(session: AsyncSession):
    """Open an isolated transaction or savepoint for the supplied session."""

    transaction = session.begin_nested() if session.in_transaction() else session.begin()
    async with transaction:
        yield


class SessionTransactionService:
    """Create validated BUY transaction sessions without exposing session IDs."""

    def __init__(
        self,
        session: AsyncSession,
        repository: SessionTransactionRepository,
        item_service: ItemService,
        lot_service: LotService,
        material_service: MaterialService | None = None,
    ) -> None:
        self._session = session
        self._repository = repository
        self._item_service = item_service
        self._lot_service = lot_service
        self._material_service = material_service

    async def create_buy_stackable(
        self,
        *,
        user_id: UUID,
        quantity: int,
        item_id: UUID,
        kind: str,
        fee: Decimal | None,
        ttc: Decimal,
        type_detail: SessionTransactionTypeDetail,
    ) -> Session:
        """Create a stackable BUY line with quantity and no lot reference."""

        if quantity < 1:
            raise UnprocessingError("Quantity must be at least 1")
        stackable = await self._item_service.is_item_stackable(item_id=item_id)
        if stackable is None:
            raise AppError(404, "Item not found")
        if not stackable:
            raise UnprocessingError("Item is not stackable")
        
        item = await self._item_service.get_item_with_economy(item_id=item_id)
        if item is None:
            raise AppError(404, "Item not found")
        if item.economy is None or item.economy.tt is None:
            raise UnprocessingError("Item has no TT value")
        
        tt = item.economy.tt * quantity
        
        async with _transaction_scope(self._session):
            transaction_session, line = await self._repository.create_buy(
                user_id=user_id, item_id=item_id, lot_id=None, quantity=quantity,
                tt=tt, fee=fee, ttc=ttc, type_detail=type_detail,
            )
            await self._lot_service.create_transaction_lot(
                user_id=user_id,
                session_line=line,
                kind=LotKind(kind.upper()),
                quantity=quantity,
                tt=tt,
            )
            return transaction_session

    async def create_buy_unstackable(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
        kind: str,
        tt: Decimal,
        fee: Decimal | None,
        ttc: Decimal,
        type_detail: SessionTransactionTypeDetail,
    ) -> Session:
        """Create a non-stackable BUY line with a lot and null quantity."""

        stackable = await self._item_service.is_item_stackable(item_id=item_id)
        if stackable is None:
            raise AppError(404, "Item not found")
        if stackable:
            raise UnprocessingError("Item is stackable")
        
        async with _transaction_scope(self._session):
            transaction_session, line = await self._repository.create_buy(
                user_id=user_id, item_id=item_id, lot_id=None, quantity=1,
                tt=tt, fee=fee, ttc=ttc, type_detail=type_detail,
            )
            await self._lot_service.create_transaction_lot(
                user_id=user_id,
                session_line=line,
                kind=LotKind(kind.upper()),
                quantity=1,
                tt=tt,
            )
            return transaction_session

    async def create_sell_stackable(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
        quantity: int,
        tt: Decimal,
        ttc: Decimal,
    ) -> Session:
        """Create a stackable SELL from active owned lots in FIFO order.

        The sale is accepted only when active available lots for the item have
        a strictly greater total quantity than the requested quantity. One
        consumed session line is persisted per source lot so every lot used by
        the sale remains identifiable.
        """

        if quantity < 1:
            raise UnprocessingError("Quantity must be at least 1")
        stackable = await self._item_service.is_item_stackable(item_id=item_id)
        if stackable is None:
            raise AppError(404, "Item not found")
        if not stackable:
            raise UnprocessingError("Item is not stackable")

        async with _transaction_scope(self._session):
            _item, lots, total_quantity = await self._lot_service.get_fifo_lots(
                user_id=user_id, item_id=item_id
            )
            if total_quantity <= quantity:
                raise UnprocessingError("Insufficient active quantity available to sell")

            allocations = await self._lot_service.allocate_fifo_quantity(
                lots=lots, quantity=quantity
            )
            lines: list[dict[str, object]] = []
            for lot, reserved_quantity in allocations:
                lines.append(
                    {
                        "lot_id": lot.id,
                        "quantity": reserved_quantity,
                    }
                )
            await self._lot_service.reserve_for_sale(lots=allocations)
            transaction_session, _lines = await self._repository.create_sell(
                user_id=user_id, lines=lines, tt=tt, fee=None, ttc=ttc
            )
            return transaction_session

    async def create_sell_unstackable(
        self,
        *,
        user_id: UUID,
        lot_id: UUID,
        tt: Decimal,
        ttc: Decimal,
    ) -> Session:
        """Create a SELL for one owned active unstackable lot.

        The lot must represent exactly one item. A positive TT is required for
        limited tools; non-limited values are accepted as the caller-provided
        TT/TTC pair because pricing representation is a front-end concern.
        """

        async with _transaction_scope(self._session):
            lot = await self._lot_service.get_unstackable_lot(
                user_id=user_id, lot_id=lot_id
            )
            if not lot.is_active or lot.qty != 1:
                raise UnprocessingError("Only one active unstackable lot can be sold")
            origin = getattr(lot, "origin", None)
            if (
                origin is not None
                and origin.item is not None
                and is_limited_item(origin.item)
                and tt <= 0
            ):
                raise UnprocessingError("TT must be greater than 0 for a limited lot")
            
            await self._lot_service.reserve_unstackable_for_sale(lot=lot)
            transaction_session, _lines = await self._repository.create_sell(
                user_id=user_id,
                lines=[{"lot_id": lot_id, "quantity": 1}],
                tt=tt,
                fee=None,
                ttc=ttc,
            )
            return transaction_session

    async def create_consumed_material(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
        quantity: int,
    ) -> Session:
        """Consume FIFO material stock with zero fee and TTC equal to TT."""

        if quantity < 1:
            raise UnprocessingError("Quantity must be at least 1")
        if self._material_service is not None:
            material_item = await self._material_service.get_by_id(item_id)
            if material_item is None:
                raise AppError(404, "Item not found")
        else:
            material = await self._item_service.is_item_material(item_id=item_id)
            if material is None:
                raise AppError(404, "Item not found")
            if not material:
                raise UnprocessingError("Only material items can be consumed")

        item = await self._item_service.get_item_with_economy(item_id=item_id)
        if item is None:
            raise AppError(404, "Item not found")
        if item.economy is None or item.economy.tt is None:
            raise UnprocessingError("Item has no TT value")
        async with _transaction_scope(self._session):
            _item, lots, total_quantity = await self._lot_service.get_fifo_lots(
                user_id=user_id, item_id=item_id
            )
            if total_quantity < quantity:
                raise UnprocessingError("Insufficient active quantity available to consume")

            lines: list[dict[str, object]] = []
            allocations = await self._lot_service.allocate_fifo_quantity(
                lots=lots, quantity=quantity
            )
            for lot, consumed_quantity in allocations:
                lines.append(
                    {
                        "lot_id": lot.id,
                        "quantity": consumed_quantity,
                    }
                )
            await self._lot_service.consume_for_consumption(lots=allocations)
            transaction_session, _lines = await self._repository.create_consumed(
                user_id=user_id,
                lines=[
                    {"lot_id": lot_id, "quantity": consumed_quantity}
                    for lot, consumed_quantity in allocations
                    for lot_id in [lot.id]
                ],
                tt=item.economy.tt * quantity,
                fee=Decimal("0"),
                ttc=item.economy.tt * quantity,
            )
            return transaction_session

    async def get_transaction_by_id(
        self, *, user_id: UUID, session_id: UUID
    ) -> SessionTransaction:
        """Return an owned transaction by its session identifier."""

        transaction = await self._repository.get_transaction_by_id(
            session_id=session_id, user_id=user_id
        )
        if transaction is None:
            raise AppError(404, "Transaction not found")
        return transaction

    async def patch_status(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        status: SessionTransactionStatus,
    ) -> SessionTransaction:
        """Patch the status of an owned RUNNING SELL transaction.

        SOLD consumes each line's reserved quantity. RETURNED releases it
        without changing stock, while CANCELLED does the same and remains
        identifiable for exclusion from future fee and price statistics.
        """

        async with _transaction_scope(self._session):
            transaction = await self.get_transaction_by_id(
                user_id=user_id, session_id=session_id
            )
            if transaction.type is not SessionTransactionType.SELL:
                raise UnprocessingError("Only SELL transactions can change status")
            if transaction.status is not SessionTransactionStatus.RUNNING:
                raise UnprocessingError("Only RUNNING transactions can change status")

            for line in transaction.session.lines:
                if line.lot_id is None or line.quantity is None:
                    raise UnprocessingError("SELL transaction line has no lot reservation")
                lot = await self._lot_service.get_lot_by_id(
                    user_id=user_id, lot_id=line.lot_id
                )
                await self._lot_service.settle_sale_lot(
                    lot=lot,
                    quantity=line.quantity,
                    sold=status is SessionTransactionStatus.SOLDED,
                )

            await self._repository.patch_status(
                transaction=transaction, status=status
            )
            return transaction


def get_session_transaction_service(session: AsyncSession) -> SessionTransactionService:
    """Build a transaction-session service with its domain dependencies."""

    return SessionTransactionService(
        session=session,
        repository=SessionTransactionRepository(session),
        item_service=get_item_service(session),
        lot_service=get_lot_service(session),
        material_service=MaterialService(MaterialRepository(session)),
    )
