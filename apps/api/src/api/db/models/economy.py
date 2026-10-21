from decimal import Decimal
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric, text
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class Economy(Base):
    __tablename__ = "economy"

    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("item.id"),
        nullable=False,
    )
    tt: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    decay: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    avg_mu_percent: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    avg_mu_plus: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
