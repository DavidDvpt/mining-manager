from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


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
