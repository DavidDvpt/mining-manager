from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .economy import Economy
    from .enhancer import Enhancer
    from .excavator import Excavator
    from .finder import Finder
    from .finder_amplifier import FinderAmplifier


class Item(Base):
    __tablename__ = "item"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    name: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    img_id: Mapped[int | None] = mapped_column(
        nullable=True,
        server_default=None,
    )
    weight: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    is_untradeable: Mapped[bool | None] = mapped_column(
        nullable=True,
        server_default=text("false"),
    )
    is_rare: Mapped[bool | None] = mapped_column(
        nullable=True,
        server_default=text("false"),
    )
    is_active: Mapped[bool | None] = mapped_column(
        nullable=True,
        server_default=text("true"),
    )
    nexus_url: Mapped[str | None] = mapped_column(
        String(),
        nullable=True,
        server_default=None,
    )
    description: Mapped[str | None] = mapped_column(
        Text(),
        nullable=True,
        server_default=None,
    )
    type_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("type.id"),
        nullable=False,
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        server_default=None,
    )
    economy: Mapped["Economy | None"] = relationship(
        back_populates="item",
        uselist=False,
    )
    enhancer: Mapped["Enhancer | None"] = relationship(
        back_populates="item",
        uselist=False,
    )
    finder: Mapped["Finder | None"] = relationship(
        back_populates="item",
        uselist=False,
    )
    excavator: Mapped["Excavator | None"] = relationship(
        back_populates="item",
        uselist=False,
    )
    finder_amplifier: Mapped["FinderAmplifier | None"] = relationship(
        back_populates="item",
        uselist=False,
    )
