"""Response schemas for enhancer catalogue endpoints."""

from decimal import Decimal

from api.db.models import EnhancerType, Tool

from .base import ApiResponseModel
from .item_schema import ItemResponse


class EnhancerDetailsResponse(ApiResponseModel):
    """Enhancer-specific data exposed under ``details``."""

    is_stackable: bool = True
    bonus: Decimal
    decay_improvement: Decimal | None
    socket: int
    tool: Tool
    type: EnhancerType


class EnhancerResponse(ItemResponse[EnhancerDetailsResponse]):
    """Flattened item response with enhancer details."""
