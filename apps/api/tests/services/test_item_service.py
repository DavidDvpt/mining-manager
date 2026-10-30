from unittest.mock import AsyncMock
from uuid import uuid4

from api.services.item_service import ItemService


async def test_is_item_stackable_delegates_to_repository():
    """Return the repository's stackability result for a requested item."""

    repository = AsyncMock()
    repository.is_item_stackable.return_value = True
    service = ItemService(repository)
    item_id = uuid4()

    result = await service.is_item_stackable(item_id=item_id)

    assert result is True
    repository.is_item_stackable.assert_awaited_once_with(item_id=item_id)


async def test_is_item_stackable_preserves_unknown_item_result():
    """Keep ``None`` so callers can distinguish an unknown item from non-stackable."""

    repository = AsyncMock()
    repository.is_item_stackable.return_value = None

    result = await ItemService(repository).is_item_stackable(item_id=uuid4())

    assert result is None


async def test_is_item_stackable_preserves_non_stackable_result():
    """Keep ``False`` for an existing item without material details."""

    repository = AsyncMock()
    repository.is_item_stackable.return_value = False

    result = await ItemService(repository).is_item_stackable(item_id=uuid4())

    assert result is False
