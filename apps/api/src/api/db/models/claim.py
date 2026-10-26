"""Mining claims associated with a mining session."""

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Integer, Numeric, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .item import Item
    from .session_mining import SessionMining


class Claim(Base):
    __tablename__ = "claims"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    session_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("session_mining.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("item.id"),
        nullable=False,
    )
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    is_hof: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )
    depth: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=5, scale=1), nullable=True, server_default=None
    )
    latitude: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default=None
    )
    longitude: Mapped[int | None] = mapped_column(
        Integer, nullable=True, server_default=None
    )
    created_at: Mapped[date] = mapped_column(
        Date, nullable=False, server_default=text("now()")
    )
    updated_at: Mapped[date | None] = mapped_column(
        Date, nullable=True, server_default=None
    )
    depleted: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    session_mining: Mapped["SessionMining"] = relationship()
    item: Mapped["Item"] = relationship()
