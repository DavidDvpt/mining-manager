"""Request and response schemas for planets and their zones."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .base import ApiResponseModel


class PlanetResponse(ApiResponseModel):
    """Serialize a planet from the read-only planet catalogue."""

    id: UUID
    name: str
    nexus_url: str | None = None
    created_at: date
    updated_at: date | None


class ZoneResponse(ApiResponseModel):
    """Serialize a zone and the planet it belongs to."""

    id: UUID
    name: str
    planet_id: UUID = Field(validation_alias="planete_id", serialization_alias="planetId")
    user_id: UUID = Field(serialization_alias="userId")
    created_at: date
    updated_at: date | None


class CreateZoneRequest(BaseModel):
    """Validate the name supplied when creating a zone for a planet."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
