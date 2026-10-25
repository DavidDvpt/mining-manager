"""Response schemas for finder catalogue endpoints."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .item_schema import ItemResponse


class FinderDetailsResponse(BaseModel):
    """Finder-specific data exposed under ``details``."""

    model_config = ConfigDict(from_attributes=True)

    use_per_minute: int | None
    depth: Decimal | None
    range: Decimal | None
    ammo_burn: int | None


class FinderResponse(ItemResponse[FinderDetailsResponse]):
    """Flattened item response with finder details."""
