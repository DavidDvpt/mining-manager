from enum import Enum
from uuid import UUID

from sqlalchemy import Enum as SqlEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class ToolCompatibilityRole(str, Enum):
    AMPLIFIER = "AMPLIFIER"
    ENHANCER = "ENHANCER"


class ToolAccessoryRelation(Base):
    __tablename__ = "tool_accessory_relation"

    tool_type_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("type.id"),
        primary_key=True,
        nullable=False,
    )
    accessory_type_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("type.id"),
        primary_key=True,
        nullable=False,
    )
    role: Mapped[ToolCompatibilityRole] = mapped_column(
        SqlEnum(
            ToolCompatibilityRole,
            name="tool_compatibility_role",
            native_enum=True,
        ),
        nullable=False,
    )
