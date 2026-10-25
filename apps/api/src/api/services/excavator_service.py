"""Business operations for excavator catalogue data."""

import logging
from uuid import UUID

from api.db.models import Excavator
from api.db.repositories import ExcavatorRepository
from api.entities import ItemEntity

logger = logging.getLogger(__name__)


class ExcavatorService:
    """Provide excavator catalogue use cases."""

    def __init__(self, repository: ExcavatorRepository) -> None:
        self._repository = repository

    async def get_all(self) -> list[ItemEntity[Excavator]]:
        logger.debug("excavator.get_all.start")
        items = await self._repository.get_all()
        logger.debug("excavator.get_all.success count=%d", len(items))
        return items

    async def get_by_id(self, item_id: UUID) -> ItemEntity[Excavator] | None:
        logger.debug("excavator.get_by_id.start item_id=%s", item_id)
        item = await self._repository.get_by_id(item_id)
        logger.debug("excavator.get_by_id.%s item_id=%s", "success" if item else "not_found", item_id)
        return item
