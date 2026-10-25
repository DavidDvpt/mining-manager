"""Response schemas for refiner catalogue endpoints."""

from pydantic import BaseModel, ConfigDict

from .item_schema import ItemResponse


class RefinerDetailsResponse(BaseModel):
    """Refiner-specific data exposed under ``details``."""

    model_config = ConfigDict(from_attributes=True)

    use_per_minute: int | None


class RefinerResponse(ItemResponse[RefinerDetailsResponse]):
    """Flattened item response with refiner details."""
