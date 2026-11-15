"""Request and response schemas for planets and their zones."""

from datetime import date
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PlanetResponse(BaseModel):
    """Serialize a planet from the read-only planet catalogue."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    name: str
    created_at: date
    updated_at: date | None


class ZoneResponse(BaseModel):
    """Serialize a zone and the planet it belongs to."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

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
