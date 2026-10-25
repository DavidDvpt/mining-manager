"""Persistence queries for finder items."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import Item
from api.db.models.finder import Finder
from api.entities import ItemEntity, build_item_entity


class FinderRepository:
    """Load finder items with their economy and finder details."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    def _query(self):
        """Build the finder aggregate query with all required relationships."""

        return (
            select(Item)
            .options(
                joinedload(Item.economy, innerjoin=True),
                joinedload(Item.finder, innerjoin=True),
            )
            .order_by(Item.name)
        )

    async def get_all(self) -> list[ItemEntity[Finder]]:
        """Return all finder items with economy and finder details loaded."""

        result = await self._session.scalars(self._query())
        return [build_item_entity(item, item.finder) for item in result.all()]

    async def get_by_id(self, item_id: UUID) -> ItemEntity[Finder] | None:
        """Return one finder item by its shared item identifier."""

        result = await self._session.scalars(
            self._query().where(Item.id == item_id),
        )
        item = result.first()
        return build_item_entity(item, item.finder) if item is not None else None
