"""Valuation response schemas."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class ValuationSessionType(str, Enum):
    """Session sources that can contribute to inventory valuation."""

    ALL = "ALL"
    MINING = "MINING"
    TRANSACTION = "TRANSACTION"


class ItemValuationResponse(BaseModel):
    """Purchase percentages for an item's owned inventory."""

    item_id: UUID
    average_purchase_percent: Decimal | None
    remaining_purchase_percent: Decimal | None
    calculated_at: datetime


class LotValuationResponse(BaseModel):
    """Purchase origin and realized profit attributed to one owned lot."""

    lot_id: UUID
    origin_session_id: UUID
    origin_session_type: str
    origin_tt: Decimal
    origin_ttc: Decimal
    generated_sell_profit: Decimal


class ItemLotsValuationResponse(BaseModel):
    """Per-lot valuation for one catalogue item."""

    item_id: UUID
    lots: list[LotValuationResponse]
    calculated_at: datetime


class SessionLotsValuationResponse(BaseModel):
    """Per-lot valuation for one source session."""

    session_id: UUID
    session_type: str
    lots: list[LotValuationResponse]
    calculated_at: datetime
