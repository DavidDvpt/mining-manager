"""Response schemas for finder amplifier catalogue endpoints."""

from decimal import Decimal

from .base import ApiResponseModel
from .item_schema import ItemResponse


class FinderAmplifierDetailsResponse(ApiResponseModel):
    """Finder amplifier-specific data exposed under ``details``."""

    efficiency: Decimal | None
    profession_level_min: Decimal | None


class FinderAmplifierResponse(ItemResponse[FinderAmplifierDetailsResponse]):
    """Flattened item response with finder amplifier details."""
