"""Schemas for session-line responses."""

from uuid import UUID
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from api.db.models import SessionLineType

from .item_schema import ItemSummaryResponse
from .session_schema import SessionResponse


class CreateProducedSessionLineRequest(BaseModel):
    """Validate a produced mining line creation payload."""

    item_id: UUID
    quantity: int = Field(ge=0)


class UpdateProducedSessionLineRequest(BaseModel):
    """Validate a produced mining line quantity update payload."""

    quantity: int = Field(ge=0)


class ConsumeEnhancerRequest(BaseModel):
    """Validate an enhancer counter increment for an open mining session."""

    quantity: Literal[1] = Field(default=1)


class SessionLineResponse(BaseModel):
    """Serialized session line, including its session and item."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    session_id: UUID
    item_id: UUID | None
    type: SessionLineType
    lot_id: UUID | None
    qty: int | None
    session: SessionResponse
    item: ItemSummaryResponse | None
