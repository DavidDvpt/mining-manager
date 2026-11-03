"""Persistence queries for mining loot."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Item, MiningLoot


class MiningLootRepository:
    """Load catalogue items that are available as mining loot."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_item(self, *, item_id: UUID) -> Item | None:
        """Return an item referenced by the mining-loot catalogue."""

        statement = (
            select(Item)
            .join(MiningLoot, MiningLoot.resource_id == Item.id)
            .where(Item.id == item_id)
            .limit(1)
        )
        return await self._session.scalar(statement)
