from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SqlEnum
from sqlalchemy import ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .item import Item


class Tool(str, Enum):
    FINDER = "FINDER"
    EXCAVATOR = "EXCAVATOR"


class EnhancerType(str, Enum):
    SKILL = "SKILL"
    DEPTH = "DEPTH"
    RANGE = "RANGE"
    SPEED = "SPEED"


class Enhancer(Base):
    __tablename__ = "enhancer"

    item_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("item.id"),
        primary_key=True,
        nullable=False,
    )
    bonus: Mapped[Decimal] = mapped_column(
        Numeric(),
        nullable=False,
    )
    decay_improvement: Mapped[Decimal | None] = mapped_column(
        Numeric(),
        nullable=True,
        server_default=None,
    )
    tool: Mapped[Tool] = mapped_column(
        SqlEnum(Tool, name="enhancer_tool", native_enum=True),
        nullable=False,
    )
    type: Mapped[EnhancerType] = mapped_column(
        SqlEnum(EnhancerType, name="enhancer_type", native_enum=True),
        nullable=False,
    )
    item: Mapped["Item"] = relationship(
        back_populates="enhancer",
    )
