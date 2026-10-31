"""Persistence operations for named transaction sessions."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import (
    Session,
    SessionLine,
    SessionLineTransaction,
    SessionLineType,
    SessionTransaction,
    SessionTransactionStatus,
    SessionTransactionType,
    SessionTransactionTypeDetail,
)


class SessionTransactionRepository:
    """Persist a transaction session and its first transaction line."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create_buy(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
        lot_id: UUID | None,
        quantity: int | None,
        tt: Decimal | None,
        fee: Decimal | None,
        ttc: Decimal,
        type_detail: SessionTransactionTypeDetail,
    ) -> tuple[Session, SessionLine]:
        """Create the session, BUY metadata, line, and price details atomically."""

        transaction_session = Session(user_id=user_id)
        transaction_session.transaction = SessionTransaction(
            type=SessionTransactionType.BUY,
            status=SessionTransactionStatus.SOLDED,
            type_detail=type_detail,
        )
        line = SessionLine(
            item_id=item_id,
            lot_id=lot_id,
            type=SessionLineType.PRODUCED,
            qty=quantity,
        )
        line.transaction = SessionLineTransaction(tt=tt, fee=fee, ttc=ttc)
        transaction_session.lines.append(line)
        self._session.add(transaction_session)
        await self._session.flush()
        return transaction_session, line
