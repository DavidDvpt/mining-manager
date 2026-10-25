"""Response schemas for enhancer catalogue endpoints."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict

from api.db.models import EnhancerType, Tool

from .item_schema import ItemResponse


class EnhancerDetailsResponse(BaseModel):
    """Enhancer-specific data exposed under ``details``."""

    model_config = ConfigDict(from_attributes=True)

    bonus: Decimal
    decay_improvement: Decimal | None
    tool: Tool
    type: EnhancerType


class EnhancerResponse(ItemResponse[EnhancerDetailsResponse]):
    """Flattened item response with enhancer details."""
