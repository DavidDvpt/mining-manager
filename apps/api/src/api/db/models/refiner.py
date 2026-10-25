"""Refiner item details."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .item import Item


class Refiner(Base):
    __tablename__ = "refiner"

    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("item.id"),
        primary_key=True,
        nullable=False,
    )
    use_per_minute: Mapped[int | None] = mapped_column(
        nullable=True,
        server_default=None,
    )
    item: Mapped["Item"] = relationship(
        back_populates="refiner",
    )
