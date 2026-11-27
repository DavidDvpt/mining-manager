"""Response schemas for finder amplifier catalogue endpoints."""

from decimal import Decimal

from .base import ApiResponseModel
from .item_schema import ItemResponse
from .lot_schema import ToolLotResponse


class FinderAmplifierDetailsResponse(ApiResponseModel):
    """Finder amplifier-specific data exposed under ``details``."""

    is_stackable: bool = False
    is_limited: bool
    efficiency: Decimal | None
    profession_level_min: Decimal | None


class FinderAmplifierResponse(ItemResponse[FinderAmplifierDetailsResponse]):
    """Flattened item response with finder amplifier details."""


class FinderAmplifierLotResponse(ToolLotResponse[FinderAmplifierResponse]):
    """An available amplifier lot with its catalogue data."""
