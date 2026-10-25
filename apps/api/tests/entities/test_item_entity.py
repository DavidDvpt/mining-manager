from dataclasses import FrozenInstanceError
from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

import pytest
from api.entities import ItemEntity, build_item_entity


def test_build_item_entity_flattens_item_and_keeps_details(item_data):
    item, economy, details = item_data

    entity = build_item_entity(item, details)

    assert isinstance(entity, ItemEntity)
    assert entity.id == item.id
    assert entity.name == item.name
    assert entity.img_id == item.img_id
    assert entity.nexus_url == item.nexus_url
    assert entity.economy is economy
    assert entity.details is details


@pytest.mark.parametrize(
    "item, details",
    [
        (SimpleNamespace(economy=None), SimpleNamespace()),
        (SimpleNamespace(economy=SimpleNamespace()), None),
    ],
)
def test_build_item_entity_rejects_incomplete_aggregate(item, details):
    with pytest.raises(RuntimeError, match="missing economy data"):
        build_item_entity(item, details)


def test_item_entity_is_immutable(item_data):
    item, _economy, details = item_data
    entity = build_item_entity(item, details)

    with pytest.raises(FrozenInstanceError):
        cast(Any, entity).name = "Changed"


def test_item_entity_preserves_uuid_and_generic_details(item_data):
    item, _economy, details = item_data
    item.id = uuid4()

    entity = build_item_entity(item, details)

    assert entity.id == item.id
    assert entity.details is details
