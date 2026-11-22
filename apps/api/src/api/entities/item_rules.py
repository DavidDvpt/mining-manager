"""Domain rules shared by item entities and services."""

from api.db.models import Item


def is_limited_item(item: Item) -> bool:
    """Return whether the catalogue name marks an item as limited."""

    return item.name.endswith("(L)")
