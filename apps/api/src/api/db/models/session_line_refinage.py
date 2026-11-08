"""Mining-line reference attached to a refining session line."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .session_line import SessionLine


class SessionLineRefinage(Base):
    """Link one refining line to the produced mining line it uses."""

    __tablename__ = "session_line_refinage"

    session_line_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session_line.id", ondelete="CASCADE"),
        primary_key=True,
    )
    session_line_used_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session_line.id", ondelete="RESTRICT"),
        nullable=False,
    )

    session_line: Mapped["SessionLine"] = relationship(
        foreign_keys=[session_line_id], back_populates="refinage"
    )
    session_line_used: Mapped["SessionLine"] = relationship(
        foreign_keys=[session_line_used_id]
    )
