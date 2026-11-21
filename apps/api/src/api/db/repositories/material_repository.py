"""Persistence queries for material items."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import Item, Material
from api.entities import ItemEntity, build_item_entity


class MaterialRepository:
    """Load material items with their economy and details."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _query(self):
        """Build the material query with all data required by its response."""

        return select(Item).options(
            joinedload(Item.economy, innerjoin=True),
            joinedload(Item.material, innerjoin=True).joinedload(
                Material.material_type, innerjoin=True
            ),
        ).order_by(Item.name)

    async def get_all(self) -> list[ItemEntity[Material]]:
        """Return all materials with economy and material-type details loaded."""

        result = await self._session.scalars(self._query())
        return [build_item_entity(item, item.material) for item in result.all()]

    async def get_by_id(self, item_id: UUID) -> ItemEntity[Material] | None:
        """Return one material by item ID, or ``None`` when it does not exist."""

        result = await self._session.scalars(self._query().where(Item.id == item_id))
        item = result.first()
        return build_item_entity(item, item.material) if item is not None else None
