"""Response schemas for deposit sizes."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class DepositSizeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    size: int
    roman_size: str = Field(serialization_alias="romanSize")
    size_label: str = Field(serialization_alias="sizeLabel")
    min: Decimal
    max: Decimal
