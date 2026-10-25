"""Business operations for finder catalogue data."""

import logging
from uuid import UUID

from api.db.models.finder import Finder
from api.db.repositories import FinderRepository
from api.entities import ItemEntity

logger = logging.getLogger(__name__)


class FinderService:
    """Provide finder catalogue use cases."""

    def __init__(self, repository: FinderRepository) -> None:
        self._repository = repository

    async def get_all(self) -> list[ItemEntity[Finder]]:
        """Return all finders from the catalogue."""

        logger.debug("finder.get_all.start")
        finders = await self._repository.get_all()
        logger.debug("finder.get_all.success count=%d", len(finders))
        return finders

    async def get_by_id(self, item_id: UUID) -> ItemEntity[Finder] | None:
        """Return one finder from the catalogue by item identifier."""

        logger.debug("finder.get_by_id.start item_id=%s", item_id)
        finder = await self._repository.get_by_id(item_id)
        logger.debug(
            "finder.get_by_id.%s item_id=%s",
            "success" if finder is not None else "not_found",
            item_id,
        )
        return finder
