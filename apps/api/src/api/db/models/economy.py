from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .item import Item


class Economy(Base):
    __tablename__ = "economy"

    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("item.id"),
        primary_key=True,
        nullable=False,
    )
    tt: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=5),
        nullable=True,
        server_default=None,
    )
    decay: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=5),
        nullable=True,
        server_default=None,
    )
    avg_mu_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(precision=20, scale=5),
        nullable=True,
        server_default=None,
    )
    avg_mu_plus: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    item: Mapped["Item"] = relationship(
        back_populates="economy",
    )
