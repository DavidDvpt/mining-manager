"""Persistence queries for generic sessions."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Session, SessionMining


class SessionRepository:
    """Load sessions with ownership and specialization constraints."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_mining_session_for_user(
        self, *, session_id: UUID, user_id: UUID
    ) -> Session | None:
        """Return an owned mining session by id, regardless of open state."""

        statement = (
            select(Session)
            .join(SessionMining, SessionMining.session_id == Session.id)
            .where(Session.id == session_id, Session.user_id == user_id)
            .with_for_update()
        )
        return await self._session.scalar(statement)
