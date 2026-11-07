"""Business operations for current inventory valuation."""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.db.repositories import ItemRepository
from api.db.repositories.valuation_repository import ValuationRepository
from api.schemas.valuation_schema import ValuationSessionType


class ValuationService:
    """Calculate purchase-cost percentages for owned inventory."""

    def __init__(
        self,
        repository: ValuationRepository,
        item_repository: ItemRepository,
    ) -> None:
        """Store repositories needed for valuation and item existence checks."""

        self._repository = repository
        self._item_repository = item_repository

    async def get_item_valuation(
        self,
        *,
        user_id: UUID,
        item_id: UUID,
        session_type: ValuationSessionType = ValuationSessionType.ALL,
    ) -> dict[str, UUID | Decimal | datetime | None] | None:
        """Return historical and remaining purchase percentages for one item."""

        item = await self._item_repository.get_item_with_economy(item_id=item_id)
        if item is None:
            return None
        historical, remaining = await self._repository.get_item_purchase_percentages(
            user_id=user_id,
            item_id=item_id,
            session_type=session_type.value,
        )
        return {
            "item_id": item_id,
            "average_purchase_percent": historical,
            "remaining_purchase_percent": remaining,
            "calculated_at": datetime.now(UTC),
        }


def get_valuation_service(session: AsyncSession) -> ValuationService:
    """Build a valuation service for the current database session."""

    return ValuationService(
        repository=ValuationRepository(session),
        item_repository=ItemRepository(session),
    )
