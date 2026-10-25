"""Business operations for refiner catalogue data."""

import logging
from uuid import UUID

from api.db.models import Refiner
from api.db.repositories import RefinerRepository
from api.entities import ItemEntity

logger = logging.getLogger(__name__)


class RefinerService:
    """Provide refiner catalogue use cases."""

    def __init__(self, repository: RefinerRepository) -> None:
        self._repository = repository

    async def get_all(self) -> list[ItemEntity[Refiner]]:
        logger.debug("refiner.get_all.start")
        items = await self._repository.get_all()
        logger.debug("refiner.get_all.success count=%d", len(items))
        return items

    async def get_by_id(self, item_id: UUID) -> ItemEntity[Refiner] | None:
        logger.debug("refiner.get_by_id.start item_id=%s", item_id)
        item = await self._repository.get_by_id(item_id)
        logger.debug("refiner.get_by_id.%s item_id=%s", "success" if item else "not_found", item_id)
        return item
