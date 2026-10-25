"""Response schemas for material catalogue endpoints."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .item_schema import ItemResponse


class MaterialDetailsResponse(BaseModel):
    """Material-specific data exposed under ``details``."""

    model_config = ConfigDict(from_attributes=True)

    type: UUID


class MaterialResponse(ItemResponse[MaterialDetailsResponse]):
    """Flattened item response with material details."""
