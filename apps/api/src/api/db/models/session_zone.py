"""Named zones available during a session on a planet."""

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Date, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .planet import Planet


class SessionZone(Base):
    """A named zone belonging to a planet."""

    __tablename__ = "session_zone"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    name: Mapped[str] = mapped_column(String(), nullable=False)
    planete_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("planet.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    planet: Mapped["Planet"] = relationship()
