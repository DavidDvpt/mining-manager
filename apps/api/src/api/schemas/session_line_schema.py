"""Schemas for session-line responses."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict

from api.db.models import SessionLineType

from .item_schema import ItemSummaryResponse
from .session_schema import SessionResponse


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
