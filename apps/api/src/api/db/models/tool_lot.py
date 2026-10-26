"""Tool lot specialization."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .lot import Lot


class ToolLot(Base):
    __tablename__ = "tool_lot"
    __table_args__ = (
        CheckConstraint(
            "tier >= 0 AND tier <= 10",
            name="ck_tool_lot_tier_between_0_and_10",
        ),
    )

    lot_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("lot.id", ondelete="CASCADE"),
        primary_key=True,
    )
    tier: Mapped[int | None] = mapped_column(Integer, nullable=True)

    lot: Mapped["Lot"] = relationship(back_populates="tool_lot")
