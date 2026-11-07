"""Persistence queries for current inventory valuation."""

from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any
from uuid import UUID

from sqlalchemy import String, and_, case, cast, func, literal, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import (
    Economy,
    Lot,
    Session,
    SessionLine,
    SessionLineTransaction,
    SessionLineType,
    SessionMining,
    SessionRefinage,
    SessionTransaction,
    SessionTransactionType,
)


class ValuationRepository:
    """Calculate purchase percentages from owned lots and BUY transactions."""

    def __init__(self, session: AsyncSession) -> None:
        """Store the database session used by valuation queries."""

        self._session = session

    async def get_item_purchase_percentages(
        self, *, user_id: UUID, item_id: UUID, session_type: str
    ) -> tuple[Decimal | None, Decimal | None]:
        """Return historical and remaining weighted purchase percentages.

        Historical weighting uses the original quantity of every owned lot,
        including inactive lots. BUY lots use ``ttc / tt``; produced mining or
        crafting lots use 100% because they are session gains. Remaining
        weighting uses only active, unreserved quantity.
        """

        purchase_percent = SessionLineTransaction.ttc / func.nullif(
            SessionLineTransaction.tt, 0
        )
        acquisition_percent = case(
            (SessionTransaction.type == SessionTransactionType.BUY, purchase_percent),
            (SessionLine.type == SessionLineType.PRODUCED, literal(1)),
            else_=None,
        )
        remaining_quantity = Lot.qty - Lot.reserved
        remaining_condition = and_(
            Lot.is_active.is_(True),
            remaining_quantity > 0,
        )
        remaining_cost = case(
            (remaining_condition, remaining_quantity * acquisition_percent),
            else_=None,
        )
        remaining_qty = case(
            (remaining_condition, remaining_quantity),
            else_=None,
        )
        statement = (
            select(
                (
                    func.sum(SessionLine.qty * acquisition_percent)
                    / func.nullif(func.sum(SessionLine.qty), 0)
                    * 100
                ).label("average_purchase_percent"),
                (
                    func.sum(remaining_cost)
                    / func.nullif(func.sum(remaining_qty), 0)
                    * 100
                ).label("remaining_purchase_percent"),
            )
            .select_from(Lot)
            .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
            .outerjoin(
                SessionLineTransaction,
                SessionLineTransaction.session_line_id == SessionLine.id,
            )
            .outerjoin(
                SessionTransaction,
                SessionTransaction.session_id == SessionLine.session_id,
            )
            .outerjoin(
                SessionMining,
                SessionMining.session_id == SessionLine.session_id,
            )
            .where(
                Lot.user_id == user_id,
                SessionLine.item_id == item_id,
            )
        )
        if session_type == "MINING":
            statement = statement.where(
                SessionMining.session_id.is_not(None),
                SessionLine.type == SessionLineType.PRODUCED,
            )
        elif session_type == "TRANSACTION":
            statement = statement.where(
                SessionTransaction.type == SessionTransactionType.BUY,
            )
        elif session_type != "ALL":
            statement = statement.where(or_(False))
        row = (await self._session.execute(statement)).one()
        return row.average_purchase_percent, row.remaining_purchase_percent

    async def get_lot_graph(
        self, *, user_id: UUID
    ) -> tuple[
        Sequence[Mapping[Any, Any]], Sequence[Mapping[Any, Any]]
    ]:
        """Load owned lot origins and consumed-line edges for valuation traversal."""

        lot_rows = (
            await self._session.execute(
                select(
                    Lot.id.label("lot_id"),
                    Lot.origin_id.label("origin_line_id"),
                    Lot.qty,
                    Lot.reserved,
                    SessionLine.id.label("line_id"),
                    SessionLine.item_id,
                    SessionLine.qty.label("origin_quantity"),
                    Session.id.label("session_id"),
                    SessionTransaction.type.label("transaction_type"),
                    SessionLineTransaction.tt,
                    SessionLineTransaction.ttc,
                    Economy.tt.label("economy_tt"),
                    SessionMining.session_id.label("mining_session_id"),
                    SessionRefinage.session_id.label("refinage_session_id"),
                )
                .select_from(Lot)
                .join(SessionLine, cast(SessionLine.id, String) == Lot.origin_id)
                .join(Session, Session.id == SessionLine.session_id)
                .outerjoin(SessionTransaction, SessionTransaction.session_id == Session.id)
                .outerjoin(SessionLineTransaction, SessionLineTransaction.session_line_id == SessionLine.id)
                .outerjoin(SessionMining, SessionMining.session_id == Session.id)
                .outerjoin(SessionRefinage, SessionRefinage.session_id == Session.id)
                .outerjoin(Economy, Economy.item_id == SessionLine.item_id)
                .where(Lot.user_id == user_id)
            )
        ).mappings().all()
        consumed_rows = (
            await self._session.execute(
                select(
                    SessionLine.lot_id,
                    SessionLine.session_id,
                    SessionLine.qty,
                    SessionLineTransaction.tt,
                    SessionLineTransaction.ttc,
                    SessionLineTransaction.fee,
                    SessionTransaction.type.label("transaction_type"),
                    SessionTransaction.status.label("transaction_status"),
                    SessionRefinage.session_id.label("refinage_session_id"),
                )
                .select_from(SessionLine)
                .join(Session, Session.id == SessionLine.session_id)
                .outerjoin(SessionLineTransaction, SessionLineTransaction.session_line_id == SessionLine.id)
                .outerjoin(SessionTransaction, SessionTransaction.session_id == Session.id)
                .outerjoin(SessionRefinage, SessionRefinage.session_id == Session.id)
                .where(
                    Session.user_id == user_id,
                    SessionLine.type == SessionLineType.CONSUMED,
                    SessionLine.lot_id.is_not(None),
                )
            )
        ).mappings().all()
        return lot_rows, consumed_rows
