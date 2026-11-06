"""Schemas for FIFO lot responses."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .item_schema import ItemSummaryResponse
from .session_line_schema import SessionLineResponse


class LotResponse(BaseModel):
    """Serialized FIFO lot with its session-line origin."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    type: str
    origin: SessionLineResponse
    qty: int
    reserved: int
    created_at: datetime
    updated_at: datetime | None
    is_active: bool


class LotCollectionResponse(BaseModel):
    """Serialized item inventory with FIFO lots and aggregate quantity."""

    item: ItemSummaryResponse
    lots: list[LotResponse]
    total_quantity: int


class UnstackableLotResponse(BaseModel):
    """Serialized unstackable lot with specialized item attributes."""

    model_config = ConfigDict(from_attributes=True)

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
