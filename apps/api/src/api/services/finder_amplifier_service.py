"""Business operations for finder amplifier catalogue data."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import FinderAmplifier
from api.db.repositories import FinderAmplifierRepository
from api.entities import ItemEntity

from .lot_service import LotService, get_lot_service

logger = logging.getLogger(__name__)


class FinderAmplifierService:
    """Provide finder amplifier catalogue use cases."""

    def __init__(
        self,
        repository: FinderAmplifierRepository,
        lot_service: LotService | None = None,
    ) -> None:
        self._repository = repository
        self._lot_service = lot_service

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

    async def get_stock(self, *, user_id: UUID) -> dict[UUID, int]:
        """Return available stock for all finder amplifier catalogue items."""

        if self._lot_service is None:
            raise RuntimeError(
                "LotService is required for finder amplifier stock queries"
            )
        amplifiers = await self.get_all()
        return await self._lot_service.get_available_quantities(
            user_id=user_id,
            item_ids=[amplifier.id for amplifier in amplifiers],
        )


def get_finder_amplifier_service(
    session: AsyncSession, lot_service: LotService | None = None
) -> FinderAmplifierService:
    """Build a finder amplifier service with optional lot-stock orchestration."""

    return FinderAmplifierService(
        FinderAmplifierRepository(session),
        lot_service=lot_service or get_lot_service(session),
    )
