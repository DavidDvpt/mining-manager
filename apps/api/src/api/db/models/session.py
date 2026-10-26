"""Mining, refining, trade, or crafting session."""

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .session_line import SessionLine
    from .session_mining import SessionMining
    from .session_refinage import SessionRefinage
    from .session_trade import SessionTrade
    from .user import User


class Session(Base):
    __tablename__ = "session"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    user_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=False,
    )
    started_at: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("now()")
    )
    ended_at: Mapped[date | None] = mapped_column(
        Date, nullable=True, server_default=None
    )
    mining: Mapped["SessionMining | None"] = relationship(
        back_populates="session", uselist=False
    )
    refinage: Mapped["SessionRefinage | None"] = relationship(
        back_populates="session", uselist=False
    )
    trade: Mapped["SessionTrade | None"] = relationship(
        back_populates="session", uselist=False
    )
    lines: Mapped[list["SessionLine"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )
    user: Mapped["User"] = relationship()
