"""Persistence operations for catalogue items."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import Item, Material


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
