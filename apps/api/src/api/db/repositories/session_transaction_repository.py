"""Persistence operations for named transaction sessions."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

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

    async def create_sell(
        self,
        *,
        user_id: UUID,
        lines: list[dict[str, object]],
    ) -> tuple[Session, list[SessionLine]]:
        """Persist a SELL session and its consumed lines atomically.

        Each input dictionary must contain ``lot_id``, ``quantity``, ``tt``
        and ``ttc``. The repository only maps validated values to persistence
        models; ownership and inventory rules remain in the service.
        """

        transaction_session = Session(user_id=user_id)
        transaction_session.transaction = SessionTransaction(
            type=SessionTransactionType.SELL,
            status=SessionTransactionStatus.RUNNING,
        )
        created_lines: list[SessionLine] = []
        for values in lines:
            line = SessionLine(
                item_id=None,
                lot_id=values["lot_id"],
                type=SessionLineType.CONSUMED,
                qty=values["quantity"],
            )
            line.transaction = SessionLineTransaction(
                tt=values["tt"],
                fee=None,
                ttc=values["ttc"],
            )
            transaction_session.lines.append(line)
            created_lines.append(line)
        self._session.add(transaction_session)
        await self._session.flush()
        return transaction_session, created_lines

    async def get_transaction_by_id(
        self, *, session_id: UUID, user_id: UUID
    ) -> SessionTransaction | None:
        """Load an owned transaction with its lines and lock it for updates."""

        statement = (
            select(SessionTransaction)
            .join(Session, Session.id == SessionTransaction.session_id)
            .options(
                joinedload(SessionTransaction.session).selectinload(Session.lines),
            )
            .where(
                SessionTransaction.session_id == session_id,
                Session.user_id == user_id,
            )
            .with_for_update(of=SessionTransaction)
        )
        return await self._session.scalar(statement)

    async def patch_status(
        self, *, transaction: SessionTransaction, status: SessionTransactionStatus
    ) -> SessionTransaction:
        """Persist a validated transaction status patch."""

        transaction.status = status
        await self._session.flush()
        return transaction
