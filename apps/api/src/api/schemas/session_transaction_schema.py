"""Request and response schemas for named transaction sessions."""

from datetime import date
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from .base import ApiResponseModel
from .item_schema import ItemSummaryResponse


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


class CreateStackableSellRequest(BaseModel):
    """Payload for a stackable SELL transaction session."""

    quantity: int = Field(ge=1)
    item_id: UUID
    tt: Decimal = Field(ge=0)
    ttc: Decimal = Field(ge=0)


class CreateConsumedMaterialRequest(BaseModel):
    """Payload for consuming stackable material inventory."""

    quantity: int = Field(ge=1)
    item_id: UUID


class CreateUnstackableSellRequest(BaseModel):
    """Payload for a non-stackable SELL transaction session."""

    quantity: Literal[1] = 1
    lot_id: UUID
    tt: Decimal = Field(ge=0)
    ttc: Decimal = Field(ge=0)


class UpdateTransactionStatusRequest(BaseModel):
    """Payload for closing or cancelling a running transaction session."""

    status: Literal["RUNNING", "SOLDED", "RETURNED", "CANCELLED"]


class RunningTransactionLotResponse(ApiResponseModel):
    """Serialized lot reservation belonging to a running transaction."""

    lot_id: UUID
    quantity: int


class RunningTransactionResponse(ApiResponseModel):
    """Serialized row displayed by the running transaction manager."""

    session_id: UUID
    type: str
    status: Literal["RUNNING", "SOLDED", "RETURNED", "CANCELLED"]
    kind: Literal["tool", "resource"]
    item: ItemSummaryResponse
    quantity: int
    lots: list[RunningTransactionLotResponse]
    created_at: date
    tt: Decimal
    ttc: Decimal


class SessionTransactionResponse(ApiResponseModel):
    """Identifier and state of a newly created transaction session."""

    session_id: UUID
    type: str
    status: str | None
