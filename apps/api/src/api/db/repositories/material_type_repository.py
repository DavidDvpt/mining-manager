"""Persistence queries for material types."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import MaterialType


class MaterialTypeRepository:
    """Load active material type catalogue entries."""

    def __init__(self, session: AsyncSession) -> None:
        """Store the database session used by material type queries."""

        self._session = session

    async def get_all(self) -> list[MaterialType]:
        """Return active material types ordered by their display name."""

        result = await self._session.scalars(
            select(MaterialType)
            .where(MaterialType.is_active.is_(True))
            .order_by(MaterialType.name)
        )
        return list(result.all())
