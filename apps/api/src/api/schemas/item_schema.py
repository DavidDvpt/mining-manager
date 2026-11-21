"""Schemas shared by item catalogue responses."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from .base import ApiResponseModel


class EconomyResponse(ApiResponseModel):
    """Economy data exposed for an item."""

    tt: Decimal | None
    decay: Decimal | None
    avg_mu_percent: Decimal | None
    avg_mu_plus: Decimal | None


class ItemSummaryResponse(ApiResponseModel):
    """Serialized catalogue item summary for nested responses."""

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


class ItemResponse[TDetails: BaseModel](ApiResponseModel):
    """Generic flattened item response."""

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
