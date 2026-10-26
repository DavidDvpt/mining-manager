"""Enhancer lot specialization."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .lot import Lot


class EnhancerLot(Base):
    __tablename__ = "enhancer_lot"

    lot_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("lot.id", ondelete="CASCADE"),
        primary_key=True,
    )

    lot: Mapped["Lot"] = relationship(back_populates="enhancer_lot")
