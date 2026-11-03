"""Business operations for generic sessions."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db.models import Session
from api.db.repositories import SessionRepository


class SessionService:
    """Provide session queries with ownership enforcement."""

    def __init__(self, repository: SessionRepository) -> None:
        self._repository = repository

    async def get_mining_session_for_user(
        self, *, session_id: UUID, user_id: UUID
    ) -> Session:
        """Return an owned mining session, whether open or closed."""

        mining_session = await self._repository.get_mining_session_for_user(
            session_id=session_id, user_id=user_id
        )
        if mining_session is None:
            raise AppError(404, "Mining session not found")
        return mining_session


def get_session_service(session: AsyncSession) -> SessionService:
    """Build a session service for the current database session."""

    return SessionService(SessionRepository(session))
