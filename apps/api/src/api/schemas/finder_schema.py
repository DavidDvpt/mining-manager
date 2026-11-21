"""Response schemas for finder catalogue endpoints."""

from decimal import Decimal

from .base import ApiResponseModel
from .item_schema import ItemResponse


class FinderDetailsResponse(ApiResponseModel):
    """Finder-specific data exposed under ``details``."""

    use_per_minute: int | None
    depth: Decimal | None
    range: Decimal | None
    ammo_burn: int | None


class FinderResponse(ItemResponse[FinderDetailsResponse]):
    """Flattened item response with finder details."""
