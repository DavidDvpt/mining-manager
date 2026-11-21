"""Response schemas for refinage recipe endpoints."""

from uuid import UUID

from .base import ApiResponseModel


class RefinageRecipeResponse(ApiResponseModel):
    """Serialize one material transformation recipe."""

    id: UUID
    result: UUID
    origin: UUID
    quantity: int
