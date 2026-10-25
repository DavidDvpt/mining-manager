"""Generic item-based read entity."""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Generic, TypeVar
from uuid import UUID

from api.db.models import Economy

TDetails = TypeVar("TDetails")


@dataclass(frozen=True, slots=True)
class ItemEntity(Generic[TDetails]):
    """An item flattened at the root and enriched with typed details."""

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
    economy: Economy
    details: TDetails
