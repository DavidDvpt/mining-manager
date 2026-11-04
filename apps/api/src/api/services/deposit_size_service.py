"""Read-only use cases for deposit sizes."""

from decimal import Decimal

from api.db.models import DepositSize
from api.db.repositories import DepositSizeRepository


class DepositSizeService:
    """Provide deposit-size catalogue use cases."""

    def __init__(self, repository: DepositSizeRepository) -> None:
        """Initialize the service with its dedicated repository."""

        self._repository = repository

    async def get_all(self) -> list[DepositSize]:
        """Return all configured deposit-size ranges."""

        return await self._repository.get_all()

    async def get_by_value(self, value: Decimal) -> DepositSize | None:
        """Return the configured range containing ``value``."""

        return await self._repository.get_by_value(value)
