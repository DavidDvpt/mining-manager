"""Persistence operations for catalogue items."""

from typing import Literal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import (
    Enhancer,
    Excavator,
    Finder,
    FinderAmplifier,
    Item,
    Material,
)

ItemCatalogueType = Literal[
    "material", "enhancer", "finder", "excavator", "finder-amplifier"
]


class ItemRepository:
    """Load catalogue item properties used by domain services."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def is_item_stackable(self, *, item_id: UUID) -> bool | None:
        """Return whether an item is stackable, or ``None`` if it is absent."""

        statement = (
            select(Item.id, Material.item_id)
            .outerjoin(Material, Material.item_id == Item.id)
            .where(Item.id == item_id)
        )
        row = (await self._session.execute(statement)).first()
        if row is None:
            return None
        return row[1] is not None

    async def is_item_material(self, *, item_id: UUID) -> bool | None:
        """Return whether an item exists and has a material catalogue row."""

        statement = (
            select(Item.id, Material.item_id)
            .outerjoin(Material, Material.item_id == Item.id)
            .where(Item.id == item_id)
        )
        row = (await self._session.execute(statement)).first()
        if row is None:
            return None
        return row[1] is not None

    async def get_item_with_economy(self, *, item_id: UUID) -> Item | None:
        """Load an item with its catalogue TT value for transaction pricing."""

        statement = (
            select(Item)
            .options(joinedload(Item.economy))
            .where(Item.id == item_id)
        )
        return await self._session.scalar(statement)

    async def is_item_of_type(
        self, *, item_id: UUID, item_type: ItemCatalogueType
    ) -> bool:
        """Return whether an item belongs to the requested catalogue type."""

        catalogue_columns = {
            "material": Material.item_id,
            "enhancer": Enhancer.item_id,
            "finder": Finder.item_id,
            "excavator": Excavator.item_id,
            "finder-amplifier": FinderAmplifier.item_id,
        }
        catalogue_column = catalogue_columns[item_type]
        statement = (
            select(Item.id)
            .outerjoin(Material, Material.item_id == Item.id)
            .outerjoin(Enhancer, Enhancer.item_id == Item.id)
            .outerjoin(Finder, Finder.item_id == Item.id)
            .outerjoin(Excavator, Excavator.item_id == Item.id)
            .outerjoin(FinderAmplifier, FinderAmplifier.item_id == Item.id)
            .where(Item.id == item_id, catalogue_column.is_not(None))
        )
        return (await self._session.scalar(statement)) is not None
