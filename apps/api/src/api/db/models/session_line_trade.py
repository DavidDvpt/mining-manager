"""Trade values attached to a session line."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .session_line import SessionLine


class SessionLineTrade(Base):
    __tablename__ = "session_line_trade"

    session_line_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session_line.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tt: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=5), nullable=False
    )
    ttc: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=5), nullable=False
    )
    fee: Mapped[Decimal] = mapped_column(
        Numeric(precision=5, scale=2), nullable=False
    )

    session_line: Mapped["SessionLine"] = relationship(back_populates="trade")
