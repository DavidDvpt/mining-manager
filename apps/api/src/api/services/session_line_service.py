"""Business operations for session lines."""

from contextlib import asynccontextmanager
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import SessionLine, SessionLineType
from api.db.repositories import SessionLineRepository
from api.services.mining_loot_service import (
    MiningLootService,
    get_mining_loot_service,
)
from api.services.session_service import SessionService, get_session_service


@asynccontextmanager
async def _transaction_scope(session: AsyncSession):
    """Open a transaction or savepoint for a session-line operation."""

    transaction = session.begin_nested() if session.in_transaction() else session.begin()
    async with transaction:
        yield


class SessionLineService:
    """Provide session-line queries with ownership enforcement."""

    def __init__(
        self,
        repository: SessionLineRepository,
        session_service: SessionService | None = None,
        mining_loot_service: MiningLootService | None = None,
    ) -> None:
        self._repository = repository
        self._session_service = session_service or get_session_service(
            repository.session
        )
        self._mining_loot_service = mining_loot_service or get_mining_loot_service(
            repository.session
        )

    async def _get_open_produced_line(
        self,
        *,
        session_id: UUID,
        session_line_id: UUID,
        user_id: UUID,
    ) -> SessionLine:
        """Load an owned produced line from an open mining session."""

        mining_session = await self._session_service.get_mining_session_for_user(
            session_id=session_id, user_id=user_id
        )
        if mining_session.ended_at is not None:
            raise UnprocessingError("The mining session is closed")

        line = await self._repository.get_session_line_for_user(
            session_id=session_id,
            session_line_id=session_line_id,
            user_id=user_id,
        )
        if line is None or line.type is not SessionLineType.PRODUCED:
            raise AppError(404, "Produced session line not found")
        return line

    async def create_produced_line(
        self,
        *,
        session_id: UUID,
        item_id: UUID,
        quantity: int,
        user_id: UUID,
    ) -> SessionLine:
        """Create an owned produced line for an open mining session."""

        async with _transaction_scope(self._repository.session):
            mining_session = await self._session_service.get_mining_session_for_user(
                session_id=session_id, user_id=user_id
            )
            if mining_session.ended_at is not None:
                raise UnprocessingError("The mining session is closed")

            item = await self._mining_loot_service.get_item(item_id=item_id)
            if item is None:
                raise AppError(404, "Item is not available as mining loot")
            return await self._repository.create_produced_line(
                session=mining_session, item=item, quantity=quantity
            )

    async def update_produced_line_quantity(
        self,
        *,
        session_id: UUID,
        session_line_id: UUID,
        quantity: int,
        user_id: UUID,
    ) -> SessionLine:
        """Update only the quantity of an owned produced mining line."""

        async with _transaction_scope(self._repository.session):
            line = await self._get_open_produced_line(
                session_id=session_id,
                session_line_id=session_line_id,
                user_id=user_id,
            )
            return await self._repository.update_quantity(
                line=line, quantity=quantity
            )

    async def delete_produced_line(
        self,
        *,
        session_id: UUID,
        session_line_id: UUID,
        user_id: UUID,
    ) -> None:
        """Delete an owned produced line that has no originating lot."""

        async with _transaction_scope(self._repository.session):
            line = await self._get_open_produced_line(
                session_id=session_id,
                session_line_id=session_line_id,
                user_id=user_id,
            )
            if await self._repository.has_origin_lot(session_line_id=line.id):
                raise UnprocessingError(
                    "A produced line with an originating lot cannot be deleted"
                )

            await self._repository.delete_line(line=line)

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

    return SessionLineService(
        SessionLineRepository(session),
        get_session_service(session),
        get_mining_loot_service(session),
    )
