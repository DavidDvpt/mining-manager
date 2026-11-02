from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Integer, Numeric
from sqlalchemy import Enum as SqlEnum
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
    __table_args__ = (
        CheckConstraint(
            "socket >= 1 AND socket <= 10",
            name="ck_enhancer_socket_between_1_and_10",
        ),
    )

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
    socket: Mapped[int] = mapped_column(Integer, nullable=False)
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
