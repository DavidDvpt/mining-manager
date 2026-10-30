"""Schemas for session responses."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class SessionResponse(BaseModel):
    """Serialized session data."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    started_at: date
    ended_at: date | None
