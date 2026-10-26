"""Mining deposit size thresholds."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import CheckConstraint, Integer, Numeric, String
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class DepositSize(Base):
    __tablename__ = "deposit_size"
    __table_args__ = (
        CheckConstraint("min >= 0", name="ck_deposit_size_min_non_negative"),
        CheckConstraint("max >= min", name="ck_deposit_size_max_gte_min"),
    )

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()"),
    )
    size: Mapped[int] = mapped_column(Integer, nullable=False)
    roman_size: Mapped[str] = mapped_column(String(10), nullable=False)
    size_label: Mapped[str] = mapped_column(String(50), nullable=False)
    min: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2), nullable=False
    )
    max: Mapped[Decimal] = mapped_column(
        Numeric(precision=20, scale=2), nullable=False
    )
