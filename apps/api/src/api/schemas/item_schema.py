"""Schemas shared by item catalogue responses."""

from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class EconomyResponse(BaseModel):
    """Economy data exposed for an item."""

    model_config = ConfigDict(from_attributes=True)

    tt: Decimal | None
    decay: Decimal | None
    avg_mu_percent: Decimal | None
    avg_mu_plus: Decimal | None


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
