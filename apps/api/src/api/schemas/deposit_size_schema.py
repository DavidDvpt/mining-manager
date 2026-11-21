"""Response schemas for deposit sizes."""

from decimal import Decimal
from uuid import UUID

from pydantic import Field

from .base import ApiResponseModel


class DepositSizeResponse(ApiResponseModel):

    id: UUID
    size: int
    roman_size: str = Field(serialization_alias="romanSize")
    size_label: str = Field(serialization_alias="sizeLabel")
    min: Decimal
    max: Decimal
