"""Business operations for finder catalogue data."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import Lot
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

    async def get_owned_lot(self, *, user_id: UUID, lot_id: UUID) -> Lot:
        """Return an owned lot after confirming that it contains a finder."""

        if self._lot_service is None:
            raise RuntimeError("LotService is required for finder lot queries")
        lot = await self._lot_service.get_unstackable_lot(
            user_id=user_id, lot_id=lot_id
        )
        if lot.origin is None or lot.origin.item is None:
            raise AppError(404, "Finder lot not found")
        if lot.origin.item.finder is None:
            raise UnprocessingError("A finder lot is required")
        return lot


def get_finder_service(
    session: AsyncSession, lot_service: LotService | None = None
) -> FinderService:
    """Build a finder service with optional lot-stock orchestration."""

    return FinderService(
        FinderRepository(session),
        lot_service=lot_service or get_lot_service(session),
    )
