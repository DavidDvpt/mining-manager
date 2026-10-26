"""Decay value attached to a session line."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .session_line import SessionLine


class SessionLineDecay(Base):
    __tablename__ = "session_line_decay"

    session_line_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session_line.id", ondelete="CASCADE"),
        primary_key=True,
    )
    decay_ttc: Mapped[Decimal] = mapped_column(
        Numeric(precision=12, scale=5), nullable=False
    )

    session_line: Mapped["SessionLine"] = relationship(back_populates="decay")
