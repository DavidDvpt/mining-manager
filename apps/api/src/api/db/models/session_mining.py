"""Mining session specialization."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum as SqlEnum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .session_mining_search_type import SessionMiningSearchType

if TYPE_CHECKING:
    from .session import Session


class SessionMining(Base):
    __tablename__ = "session_mining"
    __table_args__ = (
        CheckConstraint("clic > 0", name="ck_session_mining_clic_positive"),
    )

    session_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session.id", ondelete="CASCADE"),
        primary_key=True,
    )
    session_zone_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session_zone.id", ondelete="CASCADE"),
        nullable=True,
    )
    search_type: Mapped[SessionMiningSearchType] = mapped_column(
        SqlEnum(SessionMiningSearchType, name="session_mining_search_type"),
        nullable=False,
    )
    clic: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="mining")
