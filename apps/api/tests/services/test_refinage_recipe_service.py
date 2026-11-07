from unittest.mock import AsyncMock
from uuid import uuid4

from api.services import RefinageRecipeService


async def test_get_by_origin_delegates_to_repository():
    """Delegate origin filtering to the recipe repository."""

    repository = AsyncMock()
    expected = [object(), object()]
    repository.get_by_origin.return_value = expected
    origin_id = uuid4()

    returned = await RefinageRecipeService(repository).get_by_origin(origin_id)

    assert returned == expected
    repository.get_by_origin.assert_awaited_once_with(origin_id)
