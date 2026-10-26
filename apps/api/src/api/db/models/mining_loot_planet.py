"""Many-to-many relation between mining loot and planets."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .mining_loot import MiningLoot
    from .planet import Planet


class MiningLootPlanet(Base):
    __tablename__ = "mining_loot_planet"

    planet_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("planet.id", ondelete="CASCADE"),
        primary_key=True,
    )
    mining_loot_id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        ForeignKey("mining_loot.id", ondelete="CASCADE"),
        primary_key=True,
    )

    planet: Mapped["Planet"] = relationship(back_populates="mining_loot_links")
    mining_loot: Mapped["MiningLoot"] = relationship(
        back_populates="planet_links"
    )
