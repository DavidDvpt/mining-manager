"""Schemas for session responses."""

from datetime import date
from uuid import UUID

from .base import ApiResponseModel


class SessionResponse(ApiResponseModel):
    """Serialized session data."""

    id: UUID
    user_id: UUID
    started_at: date
    ended_at: date | None
