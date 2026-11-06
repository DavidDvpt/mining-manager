"""Response schemas for refinage recipe endpoints."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RefinageRecipeResponse(BaseModel):
    """Serialize one material transformation recipe."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    result: UUID
    origin: UUID
    quantity: int
