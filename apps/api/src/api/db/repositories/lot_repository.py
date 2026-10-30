"""Persistence operations for inventory lots."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import String, cast, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import (
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
            self._session.add(ToolLot(lot_id=lot.id, tt=tt))
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
            .with_for_update()
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
                joinedload(Lot.origin).joinedload(SessionLine.item),
                joinedload(Lot.tool_lot),
                joinedload(Lot.material_lot),
                joinedload(Lot.enhancer_lot),
            )
            .where(Lot.id == lot_id, Lot.user_id == user_id)
        )
        return await self._session.scalar(statement)

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
            select(Lot)
            .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
            .join(Session, Session.id == SessionLine.session_id)
            .join(Item, Item.id == SessionLine.item_id)
            .options(
                joinedload(Lot.origin).joinedload(SessionLine.session),
                joinedload(Lot.origin).joinedload(SessionLine.item),
            )
            .where(
                Lot.user_id == user_id,
                Item.id == item_id,
                Lot.is_active.is_(True),
                Lot.qty - Lot.reserved > 0,
            )
            .order_by(Lot.created_at.asc(), Lot.id.asc())
        )
        result = await self._session.scalars(statement)
        lots = list(result.unique().all())
        return item, lots, sum(lot.qty - lot.reserved for lot in lots)
