"""Persistence operations for inventory lots."""

from collections.abc import Collection
from decimal import Decimal
from uuid import UUID

from sqlalchemy import String, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import (
    Enhancer,
    EnhancerLot,
    Item,
    Lot,
    LotType,
    MaterialLot,
    Session,
    SessionLine,
    ToolLot,
)


class LotRepository:
    """Persist inventory lots and their database-specific relationships."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: UUID,
        session_line: SessionLine,
        kind: str,
        quantity: int,
        tt: Decimal | None,
    ) -> Lot:
        """Persist the base lot and exactly one specialized lot row.

        The caller must already have validated the session line and the
        domain-specific payload rules. This method only performs persistence;
        the surrounding service transaction commits both inserts atomically.
        """

        lot = Lot(
            user_id=user_id,
            type=LotType.TRANSACTION,
            origin_id=str(session_line.id),
            qty=quantity,
            is_active=True,
        )
        self._session.add(lot)
        await self._session.flush()

        if kind == "TOOL":
            self._session.add(ToolLot(lot_id=lot.id, tt=tt, is_default=False))
        elif kind == "ENHANCER":
            self._session.add(EnhancerLot(lot_id=lot.id))
        else:
            self._session.add(MaterialLot(lot_id=lot.id))

        await self._session.flush()
        return lot

    async def get_origin_with_item(
        self, *, user_id: UUID, lot_id: UUID
    ) -> Lot | None:
        """Load an owned lot with its origin item while locking the lot row.

        The row lock makes the quantity and reservation checks performed by the
        service safe when concurrent operations target the same lot.
        """

        statement = (
            select(Lot)
            .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
            .options(joinedload(Lot.origin).joinedload(SessionLine.item))
            .where(Lot.id == lot_id, Lot.user_id == user_id)
            .with_for_update(of=Lot)
        )
        return await self._session.scalar(statement)

    async def get_unstackable_lot(
        self, *, user_id: UUID, lot_id: UUID
    ) -> Lot | None:
        """Load an owned unstackable lot with specialized item details."""

        statement = (
            select(Lot)
            .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
            .options(
                joinedload(Lot.origin)
                .joinedload(SessionLine.item)
                .joinedload(Item.finder),
                joinedload(Lot.origin)
                .joinedload(SessionLine.item)
                .joinedload(Item.excavator),
                joinedload(Lot.origin)
                .joinedload(SessionLine.item)
                .joinedload(Item.refiner),
                joinedload(Lot.tool_lot),
                joinedload(Lot.material_lot),
                joinedload(Lot.enhancer_lot),
            )
            .where(Lot.id == lot_id, Lot.user_id == user_id)
            .with_for_update(of=Lot)
        )
        return await self._session.scalar(statement)

    async def update_tool_lot(
        self, *, lot: Lot, tier: int | None, tt: Decimal | None, is_active: bool
    ) -> Lot:
        """Persist validated tool attributes and active state."""

        if lot.tool_lot is not None:
            lot.tool_lot.tier = tier
            lot.tool_lot.tt = tt
        lot.is_active = is_active
        await self._session.flush()
        return lot

    async def get_tool_lot_for_default(
        self, *, user_id: UUID, lot_id: UUID
    ) -> Lot | None:
        """Lock and load an owned tool lot with eligible catalogue details."""

        statement = (
            select(Lot)
            .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
            .options(
                joinedload(Lot.origin)
                .joinedload(SessionLine.item)
                .joinedload(Item.finder),
                joinedload(Lot.origin)
                .joinedload(SessionLine.item)
                .joinedload(Item.excavator),
                joinedload(Lot.origin)
                .joinedload(SessionLine.item)
                .joinedload(Item.refiner),
                joinedload(Lot.tool_lot),
            )
            .where(Lot.id == lot_id, Lot.user_id == user_id)
            .with_for_update(of=Lot)
        )
        lot = await self._session.scalar(statement)
        return lot

    async def set_default_tool_lot(self, *, lot: Lot) -> Lot:
        """Persist the default flag on a validated, locked tool lot."""

        if lot.tool_lot is None:
            return lot
        lot.tool_lot.is_default = True
        await self._session.flush()
        return lot



    async def update_quantities(
        self, *, lot: Lot, quantity: int, reserved: int, is_active: bool
    ) -> Lot:
        """Persist validated lot quantities and active state.

        The service supplies the validated values; this method only applies
        them to the tracked entity and flushes the change in the caller's
        transaction.
        """

        lot.qty = quantity
        lot.reserved = reserved
        lot.is_active = is_active
        await self._session.flush()
        return lot

    async def get_fifo_lots_for_item(
        self, *, user_id: UUID, item_id: UUID
    ) -> tuple[Item | None, list[Lot], int]:
        """Load an item, FIFO lots with unreserved stock, and available quantity."""

        item = await self._session.scalar(select(Item).where(Item.id == item_id))
        if item is None:
            return None, [], 0

        statement = (
            self._available_lots_statement(user_id=user_id, item_id=item_id)
            .options(
                joinedload(Lot.origin).joinedload(SessionLine.session),
                joinedload(Lot.origin).joinedload(SessionLine.item),
            )
            .order_by(Lot.created_at.asc(), Lot.id.asc())
            .with_for_update(of=Lot)
        )
        result = await self._session.scalars(statement)
        lots = list(result.unique().all())
        return item, lots, sum(lot.qty - lot.reserved for lot in lots)

    def _available_lots_statement(self, *, user_id: UUID, item_id: UUID):
        """Build the shared query for active lots with available quantity."""

        return (
            select(Lot)
            .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
            .join(Session, Session.id == SessionLine.session_id)
            .join(Item, Item.id == SessionLine.item_id)
            .where(
                Lot.user_id == user_id,
                Item.id == item_id,
                Lot.is_active.is_(True),
                Lot.qty - Lot.reserved > 0,
            )
        )

    async def get_available_quantity_for_item(
        self, *, user_id: UUID, item_id: UUID
    ) -> int:
        """Return one item's active, unreserved quantity without loading lots."""

        statement = self._available_lots_statement(
            user_id=user_id,
            item_id=item_id,
        ).with_only_columns(
            func.coalesce(func.sum(Lot.qty - Lot.reserved), 0),
            maintain_column_froms=True,
        )
        return int(await self._session.scalar(statement) or 0)

    async def get_available_quantities(
        self, *, user_id: UUID, item_ids: Collection[UUID]
    ) -> dict[UUID, int]:
        """Return active, unreserved quantities grouped by requested item IDs."""

        if not item_ids:
            return {}
        statement = (
            select(SessionLine.item_id, func.sum(Lot.qty - Lot.reserved))
            .select_from(Lot)
            .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
            .where(
                Lot.user_id == user_id,
                SessionLine.item_id.in_(item_ids),
                SessionLine.item_id.is_not(None),
                Lot.is_active.is_(True),
                Lot.qty - Lot.reserved > 0,
            )
            .group_by(SessionLine.item_id)
        )
        rows = (await self._session.execute(statement)).all()
        return {
            item_id: int(quantity)
            for item_id, quantity in rows
            if item_id is not None
        }

    async def get_enhancer_lots_for_item(
        self, *, user_id: UUID, item_id: UUID
    ) -> tuple[Item | None, list[Lot], int]:
        """Return enhancer inventory through the existing FIFO query."""

        item, lots, total_quantity = await self.get_fifo_lots_for_item(
            user_id=user_id,
            item_id=item_id,
        )
        if item is None or item.enhancer is None:
            return item, [], 0
        return item, lots, total_quantity

    async def get_enhancer_stock_by_type_socket(
        self, *, user_id: UUID, enhancer_type: str, socket: int
    ) -> int:
        """Return available enhancer stock for a type/socket combination."""

        statement = (
            select(func.coalesce(func.sum(Lot.qty - Lot.reserved), 0))
            .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
            .join(Item, Item.id == SessionLine.item_id)
            .join(Enhancer, Enhancer.item_id == Item.id)
            .where(
                Lot.user_id == user_id,
                Lot.is_active.is_(True),
                Lot.qty - Lot.reserved > 0,
                Enhancer.type == enhancer_type,
                Enhancer.socket == socket,
            )
        )
        return int(await self._session.scalar(statement) or 0)
