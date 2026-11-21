"""Response schemas for refiner catalogue endpoints."""

from .base import ApiResponseModel
from .item_schema import ItemResponse


class RefinerDetailsResponse(ApiResponseModel):
    """Refiner-specific data exposed under ``details``."""

    use_per_minute: int | None


class RefinerResponse(ItemResponse[RefinerDetailsResponse]):
    """Flattened item response with refiner details."""
