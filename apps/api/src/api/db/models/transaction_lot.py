"""Links between transactions and the lot kind they affect."""

from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, Enum as SqlEnum, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .resource_lot import ResourceLot
    from .transaction import Transaction


class TransactionLotType(str, Enum):
    MATERIAL = "MATERIAL"
    TOOL = "TOOL"
    ENHANCER = "ENHANCER"


class TransactionLot(Base):
    __tablename__ = "transaction_lot"
    __table_args__ = (
        CheckConstraint("quantity > 0", name="ck_transaction_lot_quantity_positive"),
        CheckConstraint(
            "(lot_type = 'MATERIAL' AND material_lot_id IS NOT NULL "
            "AND tool_lot_id IS NULL AND enhancer_lot_id IS NULL) OR "
            "(lot_type = 'TOOL' AND material_lot_id IS NULL "
            "AND tool_lot_id IS NOT NULL AND enhancer_lot_id IS NULL) OR "
            "(lot_type = 'ENHANCER' AND material_lot_id IS NULL "
            "AND tool_lot_id IS NULL AND enhancer_lot_id IS NOT NULL)",
            name="ck_transaction_lot_single_lot_reference",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    transaction_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("transaction.id", ondelete="CASCADE"),
        nullable=False,
    )
    lot_type: Mapped[TransactionLotType] = mapped_column(
        SqlEnum(TransactionLotType, name="transaction_lot_type"),
        nullable=False,
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    material_lot_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("resource_lot.id", ondelete="RESTRICT"),
        nullable=True,
    )
    # These become real FKs when the corresponding lot tables are introduced.
    tool_lot_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=True
    )
    enhancer_lot_id: Mapped[UUID | None] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=True
    )

    transaction: Mapped["Transaction"] = relationship(back_populates="transaction_lots")
    material_lot: Mapped["ResourceLot | None"] = relationship(
        back_populates="transaction_lots",
    )
