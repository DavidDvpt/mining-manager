from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from api.services import (
    EnhancerService,
    ExcavatorService,
    FinderAmplifierService,
    FinderService,
    MaterialService,
    RefinerService,
)


@pytest.mark.parametrize(
    "service_type",
    [
        EnhancerService,
        ExcavatorService,
        FinderAmplifierService,
        FinderService,
        MaterialService,
        RefinerService,
    ],
)
async def test_get_all_delegates_to_repository(service_type):
    repository = AsyncMock()
    expected = [object(), object()]
    repository.get_all.return_value = expected

    result = await service_type(repository).get_all()

    assert result == expected
    repository.get_all.assert_awaited_once_with()


@pytest.mark.parametrize(
    "service_type",
    [
        EnhancerService,
        ExcavatorService,
        FinderAmplifierService,
        FinderService,
        MaterialService,
        RefinerService,
    ],
)
@pytest.mark.parametrize("expected", [object(), None])
async def test_get_by_id_delegates_and_returns_repository_result(service_type, expected):
    repository = AsyncMock()
    repository.get_by_id.return_value = expected
    item_id = uuid4()

    result = await service_type(repository).get_by_id(item_id)

    assert result is expected
    repository.get_by_id.assert_awaited_once_with(item_id)
