"""Business operations for session lines."""

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import SessionLine, SessionLineType
from api.db.repositories import SessionLineRepository
from api.db.repositories.enhancer_repository import EnhancerRepository
from api.services.enhancer_service import EnhancerService
from api.services.mining_loot_service import (
    MiningLootService,
    get_mining_loot_service,
)
from api.services.session_service import SessionService, get_session_service

if TYPE_CHECKING:
    from api.services.lot_service import LotService


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
        enhancer_service: "EnhancerService | None" = None,
        lot_service: "LotService | None" = None,
    ) -> None:
        self._repository = repository
        self._session_service = session_service or get_session_service(
            repository.session
        )
        self._mining_loot_service = mining_loot_service or get_mining_loot_service(
            repository.session
        )
        self._enhancer_service = enhancer_service or EnhancerService(
            EnhancerRepository(repository.session)
        )
        self._lot_service = lot_service

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

    async def increment_produced_line_for_item(
        self,
        *,
        session_id: UUID,
        item_id: UUID,
        quantity: int,
        user_id: UUID,
    ) -> SessionLine:
        """Add claim quantity to a produced line without an originating lot."""

        async with _transaction_scope(self._repository.session):
            mining_session = await self._session_service.get_mining_session_for_user(
                session_id=session_id, user_id=user_id
            )
            if mining_session.ended_at is not None:
                raise UnprocessingError("The mining session is closed")

            line = await self._repository.get_produced_line_for_item(
                session_id=session_id,
                item_id=item_id,
                user_id=user_id,
            )
            if line is None:
                item = await self._mining_loot_service.get_item(item_id=item_id)
                if item is None:
                    raise AppError(404, "Item is not available as mining loot")
                return await self._repository.create_produced_line(
                    session=mining_session,
                    item=item,
                    quantity=quantity,
                )
            if await self._repository.has_origin_lot(session_line_id=line.id):
                raise UnprocessingError(
                    "A produced line with an originating lot cannot be incremented"
                )
            return await self._repository.update_quantity(
                line=line,
                quantity=(line.qty or 0) + quantity,
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

    async def consume_enhancer(
        self,
        *,
        session_id: UUID,
        item_id: UUID,
        quantity: int,
        user_id: UUID,
    ) -> list[SessionLine]:
        """Consume enhancer units into direct lot-backed session lines.

        Existing lines are filled in FIFO order while their originating lots
        have capacity. Additional lines are created only when another lot is
        required. The operation locks the session and lots so concurrent
        counter increments cannot over-consume inventory.
        """

        if quantity != 1:
            raise UnprocessingError("Enhancer counters can only be incremented by 1")

        async with _transaction_scope(self._repository.session):
            session = await self._session_service.get_mining_session_for_user(
                session_id=session_id, user_id=user_id
            )
            if session.ended_at is not None:
                raise UnprocessingError("The mining session is closed")

            lot_service = self._lot_service
            if lot_service is None:
                from api.services.lot_service import get_lot_service

                lot_service = get_lot_service(self._repository.session)
            item, lots, _stock = await lot_service.get_fifo_lots(
                user_id=user_id,
                item_id=item_id,
            )
            self._enhancer_service.validate_item(item)
            lines = await self._repository.get_consumed_lot_lines(
                session_id=session_id
            )

            usage_by_lot = {
                line.lot_id: line
                for line in lines
                if line.lot_id is not None
            }
            remaining = quantity
            changed: list[SessionLine] = []
            for lot in lots:
                if remaining == 0:
                    break
                line = usage_by_lot.get(lot.id)
                already_used = line.qty if line is not None and line.qty else 0
                capacity = lot.qty - lot.reserved - already_used
                if capacity <= 0:
                    continue
                allocated = min(remaining, capacity)
                if line is None:
                    line = await self._repository.create_consumed_enhancer_line(
                        session=session, lot=lot, quantity=allocated
                    )
                    usage_by_lot[lot.id] = line
                else:
                    line = await self._repository.update_enhancer_quantity(
                        line=line, quantity=already_used + allocated
                    )
                changed.append(line)
                remaining -= allocated

            if remaining:
                raise UnprocessingError(
                    "Insufficient enhancer quantity available"
                )
            return changed


def get_session_line_service(session: AsyncSession) -> SessionLineService:
    """Build a session-line service for the current database session."""

    return SessionLineService(
        SessionLineRepository(session),
        get_session_service(session),
        get_mining_loot_service(session),
    )
