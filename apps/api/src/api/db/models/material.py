from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .item import Item


class Material(Base):
    __tablename__ = "material"

    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("item.id"),
        primary_key=True,
        nullable=False,
    )
    type: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("material_type.id"),
        nullable=False,
    )
    item: Mapped["Item"] = relationship(
        back_populates="material",
    )
