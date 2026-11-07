"""Business operations for enhancer catalogue data."""

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db.models import Enhancer, Item, Lot
from api.db.repositories import EnhancerRepository
from api.entities import ItemEntity

if TYPE_CHECKING:
    from .lot_service import LotService

logger = logging.getLogger(__name__)


class EnhancerService:
    """Provide enhancer catalogue use cases."""

    def __init__(
        self,
        repository: EnhancerRepository,
        lot_service: "LotService | None" = None,
    ) -> None:
        self._repository = repository
        self._lot_service = lot_service

    async def get_all(self) -> list[ItemEntity[Enhancer]]:
        logger.debug("enhancer.get_all.start")
        items = await self._repository.get_all()
        logger.debug("enhancer.get_all.success count=%d", len(items))
        return items

    async def get_by_id(self, item_id: UUID) -> ItemEntity[Enhancer] | None:
        logger.debug("enhancer.get_by_id.start item_id=%s", item_id)
        item = await self._repository.get_by_id(item_id)
        logger.debug("enhancer.get_by_id.%s item_id=%s", "success" if item else "not_found", item_id)
        return item

    async def get_stock_by_type_socket(
        self, *, user_id: UUID, enhancer_type: str, socket: int
    ) -> int:
        """Return stock for enhancers matching the requested type and socket."""

        if self._lot_service is None:
            raise RuntimeError("LotService is required for enhancer stock queries")
        item_ids = await self._repository.get_item_ids_by_type_socket(
            enhancer_type=enhancer_type,
            socket=socket,
        )
        quantities = await self._lot_service.get_available_quantities(
            user_id=user_id,
            item_ids=item_ids,
        )
        return sum(quantities.values())

    def validate_item(self, item: Item) -> Item:
        """Confirm that an ORM item belongs to the enhancer catalogue."""

        if item.enhancer is None:
            raise AppError(404, "Enhancer item not found")
        return item

    async def get_owned_lots(
        self, *, user_id: UUID, item_id: UUID
    ) -> tuple[Item, list[Lot], int]:
        """Return an enhancer item and its owned FIFO lots after type validation."""

        if self._lot_service is None:
            raise RuntimeError("LotService is required for enhancer lot queries")
        item, lots, quantity = await self._lot_service.get_fifo_lots(
            user_id=user_id,
            item_id=item_id,
        )
        return self.validate_item(item), lots, quantity


def get_enhancer_service(
    session: AsyncSession, lot_service: "LotService | None" = None
) -> EnhancerService:
    """Build an enhancer service with optional lot-stock orchestration."""

    if lot_service is None:
        from .lot_service import get_lot_service

        lot_service = get_lot_service(session)
    return EnhancerService(
        EnhancerRepository(session),
        lot_service=lot_service,
    )
