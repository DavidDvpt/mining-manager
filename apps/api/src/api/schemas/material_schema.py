"""Response schemas for material catalogue endpoints."""

from pydantic import Field

from .base import ApiResponseModel
from .item_schema import ItemResponse
from .material_type_schema import MaterialTypeResponse


class MaterialDetailsResponse(ApiResponseModel):
    """Material-specific data exposed under ``details``."""

    is_stackable: bool = True
    type: MaterialTypeResponse = Field(validation_alias="material_type")


class MaterialResponse(ItemResponse[MaterialDetailsResponse]):
    """Flattened item response with material details."""
