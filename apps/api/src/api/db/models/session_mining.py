"""Mining session specialization."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

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
    clic: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped["Session"] = relationship(back_populates="mining")
