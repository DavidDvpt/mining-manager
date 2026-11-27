"""Response schemas for excavator catalogue endpoints."""

from decimal import Decimal

from .base import ApiResponseModel
from .item_schema import ItemResponse
from .lot_schema import ToolLotResponse


class ExcavatorDetailsResponse(ApiResponseModel):
    """Excavator-specific data exposed under ``details``."""

    is_stackable: bool = False
    is_limited: bool
    use_per_minute: int | None
    efficiency: Decimal | None


class ExcavatorResponse(ItemResponse[ExcavatorDetailsResponse]):
    """Flattened item response with excavator details."""


class ExcavatorLotResponse(ToolLotResponse[ExcavatorResponse]):
    """An available excavator lot with its catalogue details."""
