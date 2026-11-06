"""Business operations for refinage recipes."""

from uuid import UUID

from api.db.models import RefinageRecipe
from api.db.repositories import RefinageRecipeRepository


class RefinageRecipeService:
    """Provide refinage recipe use cases."""

    def __init__(self, repository: RefinageRecipeRepository) -> None:
        """Store the repository used by recipe use cases."""

        self._repository = repository

    async def get_by_origin(self, origin_id: UUID) -> list[RefinageRecipe]:
        """Return every recipe using the requested origin material."""

        return await self._repository.get_by_origin(origin_id)
