"""Schemas for lot creation."""

from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from api.db.models import LotKind


class LotCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: LotKind
    session_line_id: UUID
    quantity: int = Field(gt=0)
    tt: Decimal | None = None


class LotIdResponse(BaseModel):
    id: UUID
