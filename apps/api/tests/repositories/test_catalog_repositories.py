from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from api.db.repositories import (
    EnhancerRepository,
    ExcavatorRepository,
    FinderAmplifierRepository,
    FinderRepository,
    MaterialRepository,
    RefinerRepository,
)


@pytest.mark.parametrize(
    "repository_type, detail_attribute",
    [
        (EnhancerRepository, "enhancer"),
        (ExcavatorRepository, "excavator"),
        (FinderAmplifierRepository, "finder_amplifier"),
        (FinderRepository, "finder"),
        (MaterialRepository, "material"),
        (RefinerRepository, "refiner"),
    ],
)
async def test_get_all_builds_entities_from_all_rows(
    repository_type, detail_attribute, item_data
):
    item, economy, details = item_data
    setattr(item, detail_attribute, details)
    session = MagicMock()
    session.scalars = AsyncMock()
    result = MagicMock()
    result.all.return_value = [item]
    session.scalars.return_value = result

    result = await repository_type(session).get_all()

    assert len(result) == 1
    assert result[0].id == item.id
    assert result[0].economy is economy
    assert result[0].details is details
    session.scalars.assert_awaited_once()


@pytest.mark.parametrize(
    "repository_type, detail_attribute",
    [
        (EnhancerRepository, "enhancer"),
        (ExcavatorRepository, "excavator"),
        (FinderAmplifierRepository, "finder_amplifier"),
        (FinderRepository, "finder"),
        (MaterialRepository, "material"),
        (RefinerRepository, "refiner"),
    ],
)
async def test_get_by_id_returns_entity(repository_type, detail_attribute, item_data):
    item, _, details = item_data
    setattr(item, detail_attribute, details)
    session = MagicMock()
    session.scalars = AsyncMock()
    result = MagicMock()
    result.first.return_value = item
    session.scalars.return_value = result

    result = await repository_type(session).get_by_id(item.id)

    assert result is not None
    assert result.id == item.id
    assert result.details is details
    session.scalars.assert_awaited_once()


@pytest.mark.parametrize(
    "repository_type",
    [
        EnhancerRepository,
        ExcavatorRepository,
        FinderAmplifierRepository,
        FinderRepository,
        MaterialRepository,
        RefinerRepository,
    ],
)
async def test_get_by_id_returns_none_when_row_is_missing(repository_type):
    session = MagicMock()
    session.scalars = AsyncMock()
    result = MagicMock()
    result.first.return_value = None
    session.scalars.return_value = result

    result = await repository_type(session).get_by_id(uuid4())

    assert result is None


def test_repository_queries_order_items_by_name():
    session = MagicMock()
    repository = FinderRepository(session)

    query = repository._query()

    assert "ORDER BY item.name" in str(query)
