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
