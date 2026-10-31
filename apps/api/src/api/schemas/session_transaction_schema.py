"""Request and response schemas for named transaction sessions."""

from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class CreateStackableBuyRequest(BaseModel):
    """Payload for a stackable BUY transaction session."""

    quantity: int = Field(ge=1)
    kind: Literal["tool", "enhancer", "material"]
    type_detail: Literal[
        "TT", "AUCTION", "HAND_TO_HAND", "FOUND", "GIFT", "EXISTING_STOCK", "GIVEN"
    ]
    item_id: UUID
    fee: Decimal | None = None
    ttc: Decimal


class CreateUnstackableBuyRequest(BaseModel):
    """Payload for a non-stackable BUY transaction session."""

    quantity: Literal[1] = 1
    tt: Decimal
    kind: Literal["tool", "enhancer", "material"]
    type_detail: Literal[
        "TT", "AUCTION", "HAND_TO_HAND", "FOUND", "GIFT", "EXISTING_STOCK", "GIVEN"
    ]
    item_id: UUID
    fee: Decimal | None = None
    ttc: Decimal


class SessionTransactionResponse(BaseModel):
    """Identifier and state of a newly created transaction session."""

    session_id: UUID
    type: str
    status: str
