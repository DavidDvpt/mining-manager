"""Tool lot specialization."""

from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, Numeric, text
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
    tt: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=5), nullable=True
    )
    is_default: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("false")
    )

    lot: Mapped["Lot"] = relationship(back_populates="tool_lot")
