"""Read-only persistence operations for deposit sizes."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import DepositSize


class DepositSizeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_all(self) -> list[DepositSize]:
        result = await self._session.scalars(
            select(DepositSize).order_by(DepositSize.id)
        )
        return list(result.all())
