"""Business operations for catalogue items."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Item
from api.db.repositories import ItemRepository


class ItemService:
    """Provide item-level business queries."""

    def __init__(self, repository: ItemRepository) -> None:
        self._repository = repository

    async def is_item_stackable(self, *, item_id: UUID) -> bool | None:
        """Return the stackability of an item, preserving unknown-item state."""

        return await self._repository.is_item_stackable(item_id=item_id)

    async def get_item_with_economy(self, *, item_id: UUID) -> Item | None:
        """Return an item and its economy value for transaction calculations."""

        return await self._repository.get_item_with_economy(item_id=item_id)

    async def is_item_material(self, *, item_id: UUID) -> bool | None:
        """Return whether an item exists and belongs to the material catalogue."""

        return await self._repository.is_item_material(item_id=item_id)


def get_item_service(session: AsyncSession) -> ItemService:
    """Build an item service for the current database session."""

    return ItemService(ItemRepository(session))
