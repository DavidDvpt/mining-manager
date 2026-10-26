"""Input and output lines of a session."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .session_line_type import SessionLineType

if TYPE_CHECKING:
    from .lot import Lot
    from .session import Session
    from .session_line_decay import SessionLineDecay
    from .session_line_trade import SessionLineTrade


class SessionLine(Base):
    __tablename__ = "session_line"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    session_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session.id", ondelete="CASCADE"),
        nullable=False,
    )
    type: Mapped[SessionLineType] = mapped_column(
        SqlEnum(SessionLineType, name="session_line_type"),
        nullable=False,
    )
    lot_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("lot.id", ondelete="RESTRICT"),
        nullable=True,
        default=None,
        server_default=None,
    )
    qty: Mapped[int | None] = mapped_column(
        Integer, nullable=True, default=None, server_default=None
    )

    session: Mapped["Session"] = relationship(back_populates="lines")
    lot: Mapped["Lot | None"] = relationship()
    trade: Mapped["SessionLineTrade | None"] = relationship(
        back_populates="session_line", uselist=False
    )
    decay: Mapped["SessionLineDecay | None"] = relationship(
        back_populates="session_line", uselist=False
    )
