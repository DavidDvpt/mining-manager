"""Persistence operations for session lines."""

from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import (
    Item,
    Lot,
    Session,
    SessionLine,
    SessionLineType,
)


class SessionLineRepository:
    """Load session lines within their owning session scope."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Return the database session used by this repository."""

        return self._session

    async def create_produced_line(
        self, *, session: Session, item: Item, quantity: int
    ) -> SessionLine:
        """Persist a produced line for an existing mining session."""

        line = SessionLine(
            session_id=session.id,
            item_id=item.id,
            type=SessionLineType.PRODUCED,
            qty=quantity,
            session=session,
            item=item,
        )
        self._session.add(line)
        await self._session.flush()
        return line

    async def update_quantity(
        self, *, line: SessionLine, quantity: int
    ) -> SessionLine:
        """Update only a produced line quantity under the database guard."""

        await self._session.execute(
            text("SET LOCAL app.session_line_update_mode = 'produced_qty'")
        )
        line.qty = quantity
        await self._session.flush()
        return line

    async def update_enhancer_quantity(
        self, *, line: SessionLine, quantity: int
    ) -> SessionLine:
        """Persist one validated enhancer consumption increment."""

        await self._session.execute(
            text("SET LOCAL app.session_line_update_mode = 'enhancer_qty'")
        )
        line.qty = quantity
        await self._session.flush()
        return line

    async def create_consumed_enhancer_line(
        self, *, session: Session, lot: Lot, quantity: int
    ) -> SessionLine:
        """Persist a consumed enhancer line tied directly to its inventory lot."""

        line = SessionLine(
            session_id=session.id,
            type=SessionLineType.CONSUMED,
            lot_id=lot.id,
            qty=quantity,
            session=session,
            lot=lot,
        )
        self._session.add(line)
        await self._session.flush()
        return line

    async def get_consumed_lot_lines(
        self, *, session_id: UUID
    ) -> list[SessionLine]:
        """Lock consumed lot-backed lines belonging to a session."""

        return list(
            (
                await self._session.scalars(
                    select(SessionLine)
                    .where(
                        SessionLine.session_id == session_id,
                        SessionLine.type == SessionLineType.CONSUMED,
                        SessionLine.lot_id.is_not(None),
                    )
                    .with_for_update()
                )
            ).all()
        )

    async def has_origin_lot(self, *, session_line_id: UUID) -> bool:
        """Return whether a lot was created from the supplied session line."""

        statement = (
            select(Lot.id)
            .where(Lot.origin_id == str(session_line_id))
            .limit(1)
        )
        return await self._session.scalar(statement) is not None

    async def delete_line(self, *, line: SessionLine) -> None:
        """Delete a session line after its business invariants are checked."""

        await self._session.delete(line)
        await self._session.flush()

    async def get_session_line_for_user(
        self,
        *,
        session_line_id: UUID,
        user_id: UUID,
        session_id: UUID | None = None,
    ) -> SessionLine | None:
        """Return an owned session line, optionally scoped to its session."""

        conditions = [
            SessionLine.id == session_line_id,
            Session.user_id == user_id,
        ]
        if session_id is not None:
            conditions.append(SessionLine.session_id == session_id)

        statement = (
            select(SessionLine)
            .join(Session, Session.id == SessionLine.session_id)
            .options(joinedload(SessionLine.item), joinedload(SessionLine.session))
            .where(*conditions)
            .with_for_update()
        )
        return await self._session.scalar(statement)
