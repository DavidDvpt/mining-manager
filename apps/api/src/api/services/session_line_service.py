"""Business operations for session lines."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import SessionLine
from api.db.repositories import SessionLineRepository


class SessionLineService:
    """Provide session-line queries with ownership enforcement."""

    def __init__(self, repository: SessionLineRepository) -> None:
        self._repository = repository

    async def get_session_line_for_user(
        self, *, session_line_id: UUID, user_id: UUID
    ) -> SessionLine | None:
        """Return a session line only when its parent session belongs to a user."""

        return await self._repository.get_session_line_for_user(
            session_line_id=session_line_id,
            user_id=user_id,
        )


def get_session_line_service(session: AsyncSession) -> SessionLineService:
    """Build a session-line service for the current database session."""

    return SessionLineService(SessionLineRepository(session))
