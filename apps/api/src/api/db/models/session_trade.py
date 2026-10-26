"""Trade session specialization."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .session import Session


class SessionTrade(Base):
    __tablename__ = "session_trade"

    session_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session.id", ondelete="CASCADE"),
        primary_key=True,
    )

    session: Mapped["Session"] = relationship(back_populates="trade")
