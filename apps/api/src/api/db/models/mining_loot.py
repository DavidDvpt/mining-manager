"""Resources that can be obtained while mining."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Enum as SqlEnum
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base
from .mining_loot_type import MiningLootType

if TYPE_CHECKING:
    from .mining_loot_planet import MiningLootPlanet


class MiningLoot(Base):
    __tablename__ = "mining_loot"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    type: Mapped[MiningLootType] = mapped_column(
        SqlEnum(MiningLootType, name="mining_loot_type"),
        nullable=False,
    )
    resource_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True), nullable=False
    )

    planet_links: Mapped[list["MiningLootPlanet"]] = relationship(
        back_populates="mining_loot", cascade="all, delete-orphan"
    )
