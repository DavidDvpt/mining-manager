"""Persistence operations for inventory lots."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import (
    EnhancerLot,
    Item,
    Lot,
    LotType,
    MaterialLot,
    Session,
    SessionLine,
    SessionLineType,
    ToolLot,
)


class LotRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_session_line_for_user(
        self, *, session_line_id: UUID, user_id: UUID
    ) -> SessionLine | None:
        """Return a session line only when its parent session belongs to the user.

        The item join also guarantees that the produced line references an
        existing catalogue item. Authorization remains in the repository
        query so callers cannot accidentally load another user's line.
        """

        statement = (
            select(SessionLine)
            .join(Session, Session.id == SessionLine.session_id)
            .join(Item, Item.id == SessionLine.item_id)
            .where(
                SessionLine.id == session_line_id,
                Session.user_id == user_id,
            )
        )
        return await self._session.scalar(statement)

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
