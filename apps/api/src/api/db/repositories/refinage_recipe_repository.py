"""Persistence queries for refinage recipes."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import RefinageRecipe


class RefinageRecipeRepository:
    """Load refinage recipes from the database."""

    def __init__(self, session: AsyncSession) -> None:
        """Store the database session used by recipe queries."""

        self._session = session

    async def get_by_origin(self, origin_id: UUID) -> list[RefinageRecipe]:
        """Return all recipes that consume the given origin material."""

        result = await self._session.scalars(
            select(RefinageRecipe)
            .where(RefinageRecipe.origin == origin_id)
            .order_by(RefinageRecipe.result)
        )
        return list(result.all())
