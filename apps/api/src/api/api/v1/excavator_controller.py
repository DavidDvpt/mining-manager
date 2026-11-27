"""HTTP endpoints for excavator catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas import ExcavatorResponse
from api.schemas.excavator_schema import ExcavatorLotResponse
from api.services import ExcavatorService
from api.services import get_excavator_service as build_excavator_service

router = APIRouter(tags=["excavators"])


def get_excavator_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ExcavatorService:
    return build_excavator_service(session)


@router.get("", response_model=list[ExcavatorResponse])
async def get_all_excavators(
    service: Annotated[ExcavatorService, Depends(get_excavator_service)],
):
    return await service.get_all()


@router.get("/stock", response_model=dict[UUID, int])
async def get_excavator_stock(
    current_user: CurrentUser,
    service: Annotated[ExcavatorService, Depends(get_excavator_service)],
) -> dict[UUID, int]:
    """Return available excavator stock grouped by catalogue item ID."""

    return await service.get_stock(user_id=current_user["id"])


@router.get("/lots", response_model=dict[UUID, list[ExcavatorLotResponse]])
async def get_available_excavator_lots(
    current_user: CurrentUser,
    service: Annotated[ExcavatorService, Depends(get_excavator_service)],
) -> dict[UUID, list[ExcavatorLotResponse]]:
    """Return the authenticated user's available excavator lots grouped by catalogue ID."""

    inventory = await service.get_available_lots(user_id=current_user["id"])
    return {
        item_id: [
            ExcavatorLotResponse(
                id=lot.id,
                user_id=lot.user_id,
                type=lot.type.value,
                item=ExcavatorResponse.model_validate(excavator),
                qty=lot.qty,
                reserved=lot.reserved,
                tier=lot.tool_lot.tier,
                tt=lot.tool_lot.tt,
                is_default=lot.tool_lot.is_default,
                created_at=lot.created_at,
                updated_at=lot.updated_at,
                is_active=lot.is_active,
            )
            for lot, excavator in lots
        ]
        for item_id, lots in inventory.items()
    }


@router.get("/{item_id}", response_model=ExcavatorResponse)
async def get_excavator_by_id(
    item_id: UUID,
    service: Annotated[ExcavatorService, Depends(get_excavator_service)],
):
    excavator = await service.get_by_id(item_id)
    if excavator is None:
        raise AppError(status_code=404, message="Excavator not found")
    return excavator
