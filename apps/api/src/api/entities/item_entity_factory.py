"""Factories for generic item read entities."""

from typing import TypeVar

from api.db.models import Item

from .item_entity import ItemEntity

TDetails = TypeVar("TDetails")


def build_item_entity(item: Item, details: TDetails | None) -> ItemEntity[TDetails]:
    """Build an item entity from a loaded ORM item and its typed details."""

    if item.economy is None or details is None:
        raise RuntimeError("Item is missing economy data or type-specific details")

    return ItemEntity(
        id=item.id,
        name=item.name,
        img_id=item.img_id,
        weight=item.weight,
        is_untradeable=item.is_untradeable,
        is_rare=item.is_rare,
        is_active=item.is_active,
        nexus_url=item.nexus_url,
        description=item.description,
        created_at=item.created_at,
        updated_at=item.updated_at,
        economy=item.economy,
        details=details,
    )
