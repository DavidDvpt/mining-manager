"""Read-only use cases for deposit sizes."""

from api.db.models import DepositSize
from api.db.repositories import DepositSizeRepository


class DepositSizeService:
    def __init__(self, repository: DepositSizeRepository) -> None:
        self._repository = repository

    async def get_all(self) -> list[DepositSize]:
        return await self._repository.get_all()
