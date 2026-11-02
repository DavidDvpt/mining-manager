"""Request and response schemas for mining session creation."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

from api.db.models import SessionMiningSearchType

from .enhancer_schema import EnhancerDetailsResponse
from .item_schema import ItemSummaryResponse
from .lot_schema import UnstackableLotResponse


class CreateMiningSessionRequest(BaseModel):
    """Validate the tools and stackable enhancers for a mining session."""

    model_config = ConfigDict(populate_by_name=True)

    clics: int = Field(gt=0)
    search_type: SessionMiningSearchType = Field(alias="searchType")
    finder: list[UUID] = Field(min_length=1)
    session_zone: UUID | None = Field(default=None, alias="sessionZone")
    excavators: list[UUID] = Field(min_length=1)
    finder_amplifiers: list[UUID] = Field(
        default_factory=list, alias="finderAmplifiers"
    )
    finder_enhancers: dict[str, UUID] = Field(
        default_factory=dict, alias="finderEnhancers"
    )
    excavator_enhancers: dict[str, UUID] = Field(
        default_factory=dict, alias="excavatorEnhancers"
    )

    @field_validator("finder_enhancers", "excavator_enhancers")
    @classmethod
    def validate_enhancer_sockets(cls, value: dict[str, UUID]) -> dict[str, UUID]:
        """Require enhancer map keys to use the ``s1`` through ``s10`` format."""

        invalid_keys = [
            key
            for key in value
            if not key.startswith("s") or not key[1:].isdigit()
            or not 1 <= int(key[1:]) <= 10
        ]
        if invalid_keys:
            raise ValueError("Enhancer sockets must be named s1 through s10")
        return value


class CreateMiningSessionResponse(BaseModel):
    """Serialize the created mining setup and its initial cost summary."""

    model_config = ConfigDict(populate_by_name=True)

    session_id: UUID
    finder: list[UnstackableLotResponse]
    excavators: list[UnstackableLotResponse]
    finder_amplifiers: list[UnstackableLotResponse] = Field(
        alias="finderAmplifiers"
    )
    finder_enhancers: list["MiningEnhancerResponse"] = Field(
        default_factory=list, alias="finderEnhancers"
    )
    excavator_enhancers: list["MiningEnhancerResponse"] = Field(
        default_factory=list, alias="excavatorEnhancers"
    )
    cost: "MiningSessionCostResponse"


class MiningEnhancerResponse(BaseModel):
    """Serialize one enhancer socket, its catalogue item, and stock usage."""

    socket: int
    item: ItemSummaryResponse
    enhancer: EnhancerDetailsResponse
    stock: int
    used: int


class MiningSessionCostResponse(BaseModel):
    """Serialize the initial TT and markup-adjusted TTC session cost."""

    tt: Decimal
    ttc: Decimal
