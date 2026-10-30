"""Business operations for inventory lots."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import Item, Lot, LotKind, SessionLineType
from api.db.repositories import LotRepository

from .item_service import ItemService, get_item_service
from .session_line_service import SessionLineService, get_session_line_service


class LotService:
    """Provide lot creation and FIFO inventory use cases."""

    def __init__(
        self,
        session: AsyncSession,
        repository: LotRepository,
        item_service: ItemService,
        session_line_service: SessionLineService,
    ) -> None:
        self._session = session
        self._repository = repository
        self._item_service = item_service
        self._session_line_service = session_line_service

    async def create_lot(
        self,
        *,
        user_id: UUID,
        kind: LotKind,
        session_line_id: UUID,
        quantity: int,
        tt: Decimal | None,
    ) -> Lot:
        """Create a lot for an owned produced session line.

        The connected user's identifier is the lot owner. The session-line
        service verifies that the line belongs to the same user.
        """

        async with self._session.begin():
            session_line = await self._session_line_service.get_session_line_for_user(
                session_line_id=session_line_id,
                user_id=user_id,
            )
            if session_line is None:
                raise AppError(404, "Session line not found")
            if session_line.type is not SessionLineType.PRODUCED:
                raise UnprocessingError("Only produced session lines can create lots")

            if kind is LotKind.TOOL and quantity != 1:
                raise UnprocessingError("Tool quantity must be 1")
            if kind is LotKind.TOOL and tt is None:
                raise UnprocessingError("tt is required for tools")
            return await self._repository.create(
                user_id=user_id,
                session_line=session_line,
                kind=kind.value,
                quantity=quantity,
                tt=tt if kind is LotKind.TOOL else None,
            )

    async def get_fifo_lots(
        self, *, user_id: UUID, item_id: UUID
    ) -> tuple[Item, list[Lot], int]:
        """Return an item, its usable FIFO lots, and their total quantity.

        The repository enforces ownership, active status, positive quantity,
        and FIFO ordering. Non-stackable items raise HTTP 409.
        """

        stackable = await self._item_service.is_item_stackable(item_id=item_id)
        if stackable is False:
            raise UnprocessingError("Item is not stackable")
        if stackable is None:
            raise AppError(404, "Item not found")
        item, lots, total_quantity = await self._repository.get_fifo_lots_for_item(
            user_id=user_id,
            item_id=item_id,
        )
        if item is None:
            raise AppError(404, "Item not found")
        return item, lots, total_quantity


def get_lot_service(session: AsyncSession) -> LotService:
    """Build a lot service with its domain service dependencies."""

    return LotService(
        session=session,
        repository=LotRepository(session),
        item_service=get_item_service(session),
        session_line_service=get_session_line_service(session),
    )
