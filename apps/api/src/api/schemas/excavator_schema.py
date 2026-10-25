"""Response schemas for excavator catalogue endpoints."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .item_schema import ItemResponse


class ExcavatorDetailsResponse(BaseModel):
    """Excavator-specific data exposed under ``details``."""

    model_config = ConfigDict(from_attributes=True)

    use_per_minute: int | None
    efficiency: Decimal | None


class ExcavatorResponse(ItemResponse[ExcavatorDetailsResponse]):
    """Flattened item response with excavator details."""
