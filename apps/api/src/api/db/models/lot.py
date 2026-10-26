"""Base lot model."""

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum as SqlEnum, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .lot_and_session import LotAndSessionType

if TYPE_CHECKING:
    from .enhancer_lot import EnhancerLot
    from .material_lot import MaterialLot
    from .tool_lot import ToolLot


class Lot(Base):
    __tablename__ = "lot"
    __table_args__ = (
        CheckConstraint("qty >= 0", name="ck_lot_qty_non_negative"),
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    type: Mapped[LotAndSessionType] = mapped_column(
        SqlEnum(LotAndSessionType, name="lot_and_session_type"),
        nullable=False,
    )
    origin_id: Mapped[str] = mapped_column(String(), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, server_default=None
    )
    is_active: Mapped[bool] = mapped_column(
        nullable=False, server_default=text("true")
    )

    material_lot: Mapped["MaterialLot | None"] = relationship(
        back_populates="lot", uselist=False
    )
    tool_lot: Mapped["ToolLot | None"] = relationship(
        back_populates="lot", uselist=False
    )
    enhancer_lot: Mapped["EnhancerLot | None"] = relationship(
        back_populates="lot", uselist=False
    )
