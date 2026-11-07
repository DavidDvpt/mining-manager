"""HTTP endpoints for current inventory valuation."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.db.repositories.item_repository import ItemCatalogueType
from api.schemas import ItemLotsValuationResponse, ItemValuationResponse
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


async def _get_lot_valuation(
    item_id: UUID,
    current_user: dict,
    service: ValuationService,
    session_type: ValuationSessionType,
    item_type: ItemCatalogueType,
) -> ItemLotsValuationResponse:
    """Load and validate a per-lot valuation response."""

    valuation = await service.get_item_lot_valuation(
        user_id=current_user["id"],
        item_id=item_id,
        session_type=session_type,
        item_type=item_type,
    )
    if valuation is None:
        raise AppError(404, "Item not found")
    return ItemLotsValuationResponse.model_validate(valuation)


@router.get("/material/{material_id}/lots", response_model=ItemLotsValuationResponse)
async def get_material_lot_valuation(
    material_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ValuationService, Depends(valuation_service_dependency)],
    session_type: Annotated[ValuationSessionType, Query()] = ValuationSessionType.ALL,
) -> ItemLotsValuationResponse:
    """Return per-lot valuation for one material."""

    return await _get_lot_valuation(
        material_id, current_user, service, session_type, "material"
    )


@router.get("/enhancer/{enhancer_id}/lots", response_model=ItemLotsValuationResponse)
async def get_enhancer_lot_valuation(
    enhancer_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ValuationService, Depends(valuation_service_dependency)],
    session_type: Annotated[ValuationSessionType, Query()] = ValuationSessionType.ALL,
) -> ItemLotsValuationResponse:
    """Return per-lot valuation for one enhancer."""

    return await _get_lot_valuation(
        enhancer_id, current_user, service, session_type, "enhancer"
    )


@router.get("/finder/{finder_id}/lots", response_model=ItemLotsValuationResponse)
async def get_finder_lot_valuation(
    finder_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ValuationService, Depends(valuation_service_dependency)],
    session_type: Annotated[ValuationSessionType, Query()] = ValuationSessionType.ALL,
) -> ItemLotsValuationResponse:
    """Return per-lot valuation for one finder."""

    return await _get_lot_valuation(
        finder_id, current_user, service, session_type, "finder"
    )


@router.get("/excavator/{excavator_id}/lots", response_model=ItemLotsValuationResponse)
async def get_excavator_lot_valuation(
    excavator_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ValuationService, Depends(valuation_service_dependency)],
    session_type: Annotated[ValuationSessionType, Query()] = ValuationSessionType.ALL,
) -> ItemLotsValuationResponse:
    """Return per-lot valuation for one excavator."""

    return await _get_lot_valuation(
        excavator_id, current_user, service, session_type, "excavator"
    )


@router.get("/finder-amplifier/{finder_amplifier_id}/lots", response_model=ItemLotsValuationResponse)
async def get_finder_amplifier_lot_valuation(
    finder_amplifier_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ValuationService, Depends(valuation_service_dependency)],
    session_type: Annotated[ValuationSessionType, Query()] = ValuationSessionType.ALL,
) -> ItemLotsValuationResponse:
    """Return per-lot valuation for one finder amplifier."""

    return await _get_lot_valuation(
        finder_amplifier_id, current_user, service, session_type, "finder-amplifier"
    )
