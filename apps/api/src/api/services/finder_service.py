"""Business operations for finder catalogue data."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models.finder import Finder
from api.db.repositories import FinderRepository
from api.entities import ItemEntity

from .lot_service import LotService, get_lot_service

logger = logging.getLogger(__name__)


class FinderService:
    """Provide finder catalogue use cases."""

    def __init__(
        self, repository: FinderRepository, lot_service: LotService | None = None
    ) -> None:
        self._repository = repository
        self._lot_service = lot_service

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

    async def get_stock(self, *, user_id: UUID) -> dict[UUID, int]:
        """Return available stock for all finder catalogue items."""

        if self._lot_service is None:
            raise RuntimeError("LotService is required for finder stock queries")
        finders = await self.get_all()
        return await self._lot_service.get_available_quantities(
            user_id=user_id,
            item_ids=[finder.id for finder in finders],
        )


def get_finder_service(
    session: AsyncSession, lot_service: LotService | None = None
) -> FinderService:
    """Build a finder service with optional lot-stock orchestration."""

    return FinderService(
        FinderRepository(session),
        lot_service=lot_service or get_lot_service(session),
    )
