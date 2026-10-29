"""Business operations for inventory lots."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import Lot, LotKind, SessionLineType
from api.db.repositories import LotRepository


async def create_lot(
    session: AsyncSession,
    *,
    user_id: UUID,
    kind: LotKind,
    session_line_id: UUID,
    quantity: int,
    tt: Decimal | None,
) -> Lot:
    """Create a lot for an owned produced session line.

    The connected user's identifier is the lot owner. The session-line query
    verifies that the line's parent session belongs to that same user. Item
    kind compatibility is intentionally left to the transaction workflow.
    """

    async with session.begin():
        lot_repository = LotRepository(session)
        session_line = await lot_repository.get_session_line_for_user(
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
        return await lot_repository.create(
            user_id=user_id,
            session_line=session_line,
            kind=kind.value,
            quantity=quantity,
            tt=tt if kind is LotKind.TOOL else None,
        )
