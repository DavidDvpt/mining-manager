from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from api.db.repositories import ItemRepository


@pytest.mark.parametrize(
    ("row", "expected"),
    [
        ((uuid4(), uuid4()), True),
        ((uuid4(), None), False),
        (None, None),
    ],
)
async def test_is_item_stackable_maps_catalogue_row(row, expected):
    """Map material presence to stackability and preserve missing items."""

    session = MagicMock()
    result = MagicMock()
    result.first.return_value = row
    session.execute = AsyncMock(return_value=result)
    item_id = uuid4()

    actual = await ItemRepository(session).is_item_stackable(item_id=item_id)

    assert actual is expected
    session.execute.assert_awaited_once()
