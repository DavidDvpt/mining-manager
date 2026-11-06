"""Request and response schemas for mining claims."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from .deposit_size_schema import DepositSizeResponse
from .item_schema import ItemSummaryResponse


class ClaimRequest(BaseModel):
    """Validate claim fields accepted on create and partial update requests."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    item_id: UUID | None = None
    qty: int | None = Field(default=None, ge=0)
    is_hof: bool | None = None
    depth: Decimal | None = Field(default=None, ge=0)
    latitude: int | None = None
    longitude: int | None = None
    is_depleted: bool | None = Field(
        default=None,
        validation_alias=AliasChoices("isDepleted", "depleted"),
    )


class CreateClaimRequest(BaseModel):
    """Validate the required item and quantity for claim creation."""

    model_config = ConfigDict(populate_by_name=True, extra="forbid")

    item_id: UUID = Field(...)
    qty: int = Field(ge=0)
    is_hof: bool | None = None
    depth: Decimal | None = Field(default=None, ge=0)
    latitude: int | None = None
    longitude: int | None = None
    is_depleted: bool = Field(
        default=False,
        validation_alias=AliasChoices("isDepleted", "depleted"),
    )


class ClaimResponse(BaseModel):
    """Serialize a claim with its item, calculated value, and deposit size."""

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: UUID
    session_id: UUID
    item_id: UUID
    qty: int
    is_hof: bool
    depth: Decimal | None
    latitude: int | None
    longitude: int | None
    created_at: date
    updated_at: date | None
    depleted: bool
    item: ItemSummaryResponse
    value: Decimal | None = Field(
        default=None,
        validation_alias=AliasChoices("value", "calculated_value"),
    )
    deposit_size: DepositSizeResponse | None = Field(
        default=None,
        validation_alias=AliasChoices("deposit_size", "calculated_deposit_size"),
        serialization_alias="depositSize",
    )


class ClaimResultResponse(BaseModel):
    """Serialize the total claimed quantity for one item."""

    item_id: UUID
    qty: int


class ClaimCollectionResponse(BaseModel):
    """Serialize claims together with quantities aggregated by item."""

    claims: list[ClaimResponse]
    result: list[ClaimResultResponse]
