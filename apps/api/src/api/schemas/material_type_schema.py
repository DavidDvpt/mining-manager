"""Response schemas for material type catalogue endpoints."""

from uuid import UUID

from .base import ApiResponseModel


class MaterialTypeResponse(ApiResponseModel):
    """Serialize an active material type used to group material items."""

    id: UUID
    name: str
