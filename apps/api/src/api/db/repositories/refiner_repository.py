"""Persistence queries for refiner items."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import Item, Refiner
from api.entities import ItemEntity, build_item_entity


class RefinerRepository:
    """Load refiner items with their economy and details."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _query(self):
        return select(Item).options(
            joinedload(Item.economy, innerjoin=True),
            joinedload(Item.refiner, innerjoin=True),
        ).order_by(Item.name)

    async def get_all(self) -> list[ItemEntity[Refiner]]:
        result = await self._session.scalars(self._query())
        return [build_item_entity(item, item.refiner) for item in result.all()]

    async def get_by_id(self, item_id: UUID) -> ItemEntity[Refiner] | None:
        result = await self._session.scalars(self._query().where(Item.id == item_id))
        item = result.first()
        return build_item_entity(item, item.refiner) if item is not None else None
