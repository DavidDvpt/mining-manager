"""Response schemas for finder amplifier catalogue endpoints."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from .item_schema import ItemResponse


class FinderAmplifierDetailsResponse(BaseModel):
    """Finder amplifier-specific data exposed under ``details``."""

    model_config = ConfigDict(from_attributes=True)

    efficiency: Decimal | None
    profession_level_min: Decimal | None


class FinderAmplifierResponse(ItemResponse[FinderAmplifierDetailsResponse]):
    """Flattened item response with finder amplifier details."""
