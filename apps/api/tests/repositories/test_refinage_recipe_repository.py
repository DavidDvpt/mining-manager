from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from api.db.repositories import RefinageRecipeRepository


async def test_get_by_origin_returns_matching_recipes():
    """Return every recipe returned by the origin-filtered query."""

    origin_id = uuid4()
    recipes = [MagicMock(), MagicMock()]
    session = MagicMock()
    session.scalars = AsyncMock()
    result = MagicMock()
    result.all.return_value = recipes
    session.scalars.return_value = result

    returned = await RefinageRecipeRepository(session).get_by_origin(origin_id)

    assert returned == recipes
    session.scalars.assert_awaited_once()
