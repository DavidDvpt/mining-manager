"""Transactions involving user-owned resources."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Numeric, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .transaction_lot import TransactionLot
    from .user import User


class TransactionType(str, Enum):
    BUY = "BUY"
    FOUND = "FOUND"
    GIFT = "GIFT"
    EXISTING_STOCK = "EXISTING_STOCK"
    SELL = "SELL"
    GIVEN = "GIVEN"


class TransactionStatus(str, Enum):
    SOLDED = "SOLDED"
    RETURNED = "RETURNED"
    RUNNING = "RUNNING"
    CANCELED = "CANCELED"


class Transaction(Base):
    __tablename__ = "transaction"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    tt: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=5),
        nullable=False,
        server_default=text("0"),
    )
    fee: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=5),
        nullable=False,
        server_default=text("0"),
    )
    ttc: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=5),
        nullable=False,
        server_default=text("0"),
    )
    transaction_type: Mapped[TransactionType] = mapped_column(
        SqlEnum(TransactionType, name="transaction_type"),
        nullable=False,
    )
    status: Mapped[TransactionStatus | None] = mapped_column(
        SqlEnum(TransactionStatus, name="transaction_status"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )

    user: Mapped["User"] = relationship()
    transaction_lots: Mapped[list["TransactionLot"]] = relationship(
        back_populates="transaction",
    )
