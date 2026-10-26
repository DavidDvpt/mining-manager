"""Planets where mining loot can be found."""

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import UUID as PostgresUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..base import Base

if TYPE_CHECKING:
    from .mining_loot_planet import MiningLootPlanet


class Planet(Base):
    __tablename__ = "planet"

    id: Mapped[UUID] = mapped_column(
        PostgresUUID(as_uuid=True),
        primary_key=True,
        server_default="gen_random_uuid()",
    )
    name: Mapped[str] = mapped_column(String(), nullable=False)

    mining_loot_links: Mapped[list["MiningLootPlanet"]] = relationship(
        back_populates="planet", cascade="all, delete-orphan"
    )
