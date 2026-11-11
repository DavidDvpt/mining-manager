"""Response schemas for material type catalogue endpoints."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MaterialTypeResponse(BaseModel):
    """Serialize an active material type used to group material items."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
