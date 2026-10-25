"""Persistence queries for excavator items."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import Excavator, Item
from api.entities import ItemEntity, build_item_entity


class ExcavatorRepository:
    """Load excavator items with their economy and details."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _query(self):
        return select(Item).options(
            joinedload(Item.economy, innerjoin=True),
            joinedload(Item.excavator, innerjoin=True),
        ).order_by(Item.name)

    async def get_all(self) -> list[ItemEntity[Excavator]]:
        result = await self._session.scalars(self._query())
        return [build_item_entity(item, item.excavator) for item in result.all()]

    async def get_by_id(self, item_id: UUID) -> ItemEntity[Excavator] | None:
        result = await self._session.scalars(self._query().where(Item.id == item_id))
        item = result.first()
        return build_item_entity(item, item.excavator) if item is not None else None
