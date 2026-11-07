"""HTTP endpoints for current inventory valuation."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas import ItemValuationResponse
from api.schemas.valuation_schema import ValuationSessionType
from api.services import ValuationService, get_valuation_service

router = APIRouter(tags=["valuations"])


def valuation_service_dependency(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ValuationService:
    """Build the valuation service dependency from the current DB session."""

    return get_valuation_service(session)


@router.get("/item/{item_id}", response_model=ItemValuationResponse)
async def get_item_valuation(
    item_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ValuationService, Depends(valuation_service_dependency)],
    session_type: Annotated[
        ValuationSessionType, Query()
    ] = ValuationSessionType.ALL,
) -> ItemValuationResponse:
    """Return current purchase percentages for the user's owned item lots."""

    valuation = await service.get_item_valuation(
        user_id=current_user["id"],
        item_id=item_id,
        session_type=session_type,
    )
    if valuation is None:
        raise AppError(404, "Item not found")
    return ItemValuationResponse.model_validate(valuation)
