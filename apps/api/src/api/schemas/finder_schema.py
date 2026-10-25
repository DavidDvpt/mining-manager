"""Response schemas for finder catalogue endpoints."""

from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from api.db.models import EnhancerType, Tool


class EconomyResponse(BaseModel):
    """Economy data exposed for an item."""

    model_config = ConfigDict(from_attributes=True)

    tt: Decimal | None
    decay: Decimal | None
    avg_mu_percent: Decimal | None
    avg_mu_plus: Decimal | None


class FinderDetailsResponse(BaseModel):
    """Finder-specific data exposed under ``details``."""

    model_config = ConfigDict(from_attributes=True)

    use_per_minute: int | None
    depth: Decimal | None
    range: Decimal | None
    ammo_burn: int | None


TDetails = TypeVar("TDetails", bound=BaseModel)


class ItemResponse(BaseModel, Generic[TDetails]):
    """Generic flattened item response."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    img_id: int | None
    nexus_id: int | None
    weight: Decimal | None
    is_untradeable: bool | None
    is_rare: bool | None
    is_active: bool | None
    nexus_url: str | None
    description: str | None
    created_at: datetime | None
    updated_at: datetime | None
    economy: EconomyResponse
    details: TDetails


class FinderResponse(ItemResponse[FinderDetailsResponse]):
    """Flattened item response with finder details."""


class ExcavatorDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    use_per_minute: int | None
    efficiency: Decimal | None


class ExcavatorResponse(ItemResponse[ExcavatorDetailsResponse]):
    """Flattened item response with excavator details."""


class FinderAmplifierDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    efficiency: Decimal | None
    profession_level_min: Decimal | None


class FinderAmplifierResponse(ItemResponse[FinderAmplifierDetailsResponse]):
    """Flattened item response with finder amplifier details."""


class EnhancerDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bonus: Decimal
    decay_improvement: Decimal | None
    tool: Tool
    type: EnhancerType


class EnhancerResponse(ItemResponse[EnhancerDetailsResponse]):
    """Flattened item response with enhancer details."""


class MaterialDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    type: UUID


class MaterialResponse(ItemResponse[MaterialDetailsResponse]):
    """Flattened item response with material details."""


class RefinerDetailsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    use_per_minute: int | None


class RefinerResponse(ItemResponse[RefinerDetailsResponse]):
    """Flattened item response with refiner details."""
