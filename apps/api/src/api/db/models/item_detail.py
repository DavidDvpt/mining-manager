from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .item import Item


class ItemDetail(Base):
    __tablename__ = "item_detail"

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
    efficiency: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    depth: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    range: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    ammo_burn: Mapped[int | None] = mapped_column(
        nullable=True,
        server_default=None,
    )
    item: Mapped["Item"] = relationship(
        back_populates="item_detail",
    )
