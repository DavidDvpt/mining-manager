"""Transaction session specialization."""

from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum as SqlEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .session import Session


class SessionTransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    CONSUMED = "CONSUMED"


class SessionTransactionStatus(str, Enum):
    RUNNING = "RUNNING"
    RETURNED = "RETURNED"
    SOLDED = "SOLDED"
    CANCELLED = "CANCELLED"


class SessionTransactionTypeDetail(str, Enum):
    TT = "TT"
    AUCTION = "AUCTION"
    HAND_TO_HAND = "HAND_TO_HAND"
    FOUND = "FOUND"
    GIFT = "GIFT"
    EXISTING_STOCK = "EXISTING_STOCK"
    GIVEN = "GIVEN"


class SessionTransaction(Base):
    __tablename__ = "session_transaction"
    __table_args__ = (
        CheckConstraint(
            "type = 'BUY' OR type_detail IS NULL",
            name="ck_session_transaction_type_detail_buy_only",
        ),
        CheckConstraint(
            "(type = 'BUY' AND status IS NULL) "
            "OR (type <> 'BUY' AND status IS NOT NULL)",
            name="ck_session_transaction_status_by_type",
        ),
    )

    session_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session.id", ondelete="CASCADE"),
        primary_key=True,
    )

    type: Mapped[SessionTransactionType] = mapped_column(
        SqlEnum(SessionTransactionType, name="session_transaction_type"),
        nullable=False,
    )
    status: Mapped[SessionTransactionStatus | None] = mapped_column(
        SqlEnum(SessionTransactionStatus, name="session_transaction_status"),
        nullable=True,
    )
    type_detail: Mapped[SessionTransactionTypeDetail | None] = mapped_column(
        SqlEnum(
            SessionTransactionTypeDetail,
            name="session_transaction_type_detail",
        ),
        nullable=True,
    )

    session: Mapped["Session"] = relationship(back_populates="transaction")
