"""Business operations for mining loot."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Item
from api.db.repositories import MiningLootRepository


class MiningLootService:
    """Provide access to items allowed as mining loot."""

    def __init__(self, repository: MiningLootRepository) -> None:
        self._repository = repository

    async def get_item(self, *, item_id: UUID) -> Item | None:
        """Return a catalogue item if mining loot references it."""

        return await self._repository.get_item(item_id=item_id)


def get_mining_loot_service(session: AsyncSession) -> MiningLootService:
    """Build a mining-loot service for the current database session."""

    return MiningLootService(MiningLootRepository(session))
