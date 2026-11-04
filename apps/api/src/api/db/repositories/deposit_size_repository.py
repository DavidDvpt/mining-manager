"""Read-only persistence operations for deposit sizes."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import DepositSize


class DepositSizeRepository:
    """Persist and query deposit-size reference data."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the request-scoped database session."""

        self._session = session

    async def get_all(self) -> list[DepositSize]:
        """Return every deposit-size row ordered by its identifier."""

        result = await self._session.scalars(
            select(DepositSize).order_by(DepositSize.id)
        )
        return list(result.all())

    async def get_by_value(self, value: Decimal) -> DepositSize | None:
        """Return the row whose inclusive range contains ``value``."""

        return await self._session.scalar(
            select(DepositSize).where(
                DepositSize.min <= value,
                DepositSize.max >= value,
            )
        )
