"""Schemas for FIFO lot responses."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from .base import ApiResponseModel
from .item_schema import ItemSummaryResponse
from .session_line_schema import SessionLineResponse


class LotResponse(ApiResponseModel):
    """Serialized FIFO lot with its session-line origin."""

    id: UUID
    user_id: UUID
    type: str
    origin: SessionLineResponse
    qty: int
    reserved: int
    created_at: datetime
    updated_at: datetime | None
    is_active: bool


class LotCollectionResponse(ApiResponseModel):
    """Serialized item inventory with FIFO lots and aggregate quantity."""

    item: ItemSummaryResponse
    lots: list[LotResponse]
    total_quantity: int


class UnstackableLotResponse(ApiResponseModel):
    """Serialized unstackable lot with specialized item attributes."""

    id: UUID
    user_id: UUID
    type: str
    item: ItemSummaryResponse
    qty: int
    reserved: int
    tier: int | None
    tt: Decimal | None
    is_default: bool
    created_at: datetime
    updated_at: datetime | None
    is_active: bool


class UpdateUnstackableLotRequest(BaseModel):
    """Payload for changing the mutable attributes of an owned tool lot."""

    tier: int | None = Field(default=None, ge=0, le=10)
    tt: Decimal | None = Field(default=None, ge=0)
