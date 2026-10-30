"""Persistence operations for session lines."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Item, Session, SessionLine


class SessionLineRepository:
    """Load session lines within their owning session scope."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_session_line_for_user(
        self, *, session_line_id: UUID, user_id: UUID
    ) -> SessionLine | None:
        """Return a session line only when its parent session belongs to a user."""

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
