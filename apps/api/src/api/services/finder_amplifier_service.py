"""Business operations for finder amplifier catalogue data."""

import logging
from uuid import UUID

from api.db.models import FinderAmplifier
from api.db.repositories import FinderAmplifierRepository
from api.entities import ItemEntity

logger = logging.getLogger(__name__)


class FinderAmplifierService:
    """Provide finder amplifier catalogue use cases."""

    def __init__(self, repository: FinderAmplifierRepository) -> None:
        self._repository = repository

    async def get_all(self) -> list[ItemEntity[FinderAmplifier]]:
        logger.debug("finder_amplifier.get_all.start")
        items = await self._repository.get_all()
        logger.debug("finder_amplifier.get_all.success count=%d", len(items))
        return items

    async def get_by_id(self, item_id: UUID) -> ItemEntity[FinderAmplifier] | None:
        logger.debug("finder_amplifier.get_by_id.start item_id=%s", item_id)
        item = await self._repository.get_by_id(item_id)
        logger.debug("finder_amplifier.get_by_id.%s item_id=%s", "success" if item else "not_found", item_id)
        return item
