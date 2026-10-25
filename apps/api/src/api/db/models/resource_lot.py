"""Lots of resources produced, refined, or traded."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .material import Material
    from .transaction_lot import TransactionLot


class ResourceLotOrigin(str, Enum):
    MINING = "MINING"
    REFINING = "REFINING"
    TRADE = "TRADE"


class ResourceLotOriginType(str, Enum):
    TRANSACTION = "TRANSACTION"
    SESSION_LINE = "SESSION_LINE"


class ResourceLot(Base):
    __tablename__ = "resource_lot"
    __table_args__ = (
        CheckConstraint("qty >= 0", name="ck_resource_lot_qty_non_negative"),
        CheckConstraint(
            "(origin_type = 'TRANSACTION' AND transaction_id IS NOT NULL "
            "AND session_line_id IS NULL) OR "
            "(origin_type = 'SESSION_LINE' AND transaction_id IS NULL "
            "AND session_line_id IS NOT NULL)",
            name="ck_resource_lot_single_origin",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("material.item_id"),
        nullable=False,
    )
    qty: Mapped[int] = mapped_column(Integer, nullable=False)
    ratio_source: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=5),
        nullable=False,
        server_default=text("1"),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    transaction_id: Mapped[UUID | None] = mapped_column(nullable=True)
    session_line_id: Mapped[UUID | None] = mapped_column(nullable=True)
    origin: Mapped[ResourceLotOrigin] = mapped_column(
        SqlEnum(ResourceLotOrigin, name="resource_lot_origin"),
        nullable=False,
    )
    origin_type: Mapped[ResourceLotOriginType] = mapped_column(
        SqlEnum(ResourceLotOriginType, name="resource_lot_origin_type"),
        nullable=False,
    )

    material: Mapped["Material"] = relationship(back_populates="resource_lots")
    transaction_lots: Mapped[list["TransactionLot"]] = relationship(
        back_populates="material_lot",
    )
