"""HTTP endpoints for finder amplifier catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas import FinderAmplifierResponse
from api.schemas.finder_amplifier_schema import FinderAmplifierLotResponse
from api.services import FinderAmplifierService
from api.services import (
    get_finder_amplifier_service as build_finder_amplifier_service,
)

router = APIRouter(tags=["finder-amplifiers"])


def get_finder_amplifier_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FinderAmplifierService:
    return build_finder_amplifier_service(session)


@router.get("", response_model=list[FinderAmplifierResponse])
async def get_all_finder_amplifiers(
    service: Annotated[FinderAmplifierService, Depends(get_finder_amplifier_service)],
):
    return await service.get_all()


@router.get("/stock", response_model=dict[UUID, int])
async def get_finder_amplifier_stock(
    current_user: CurrentUser,
    service: Annotated[FinderAmplifierService, Depends(get_finder_amplifier_service)],
) -> dict[UUID, int]:
    """Return available amplifier stock grouped by catalogue item ID."""

    return await service.get_stock(user_id=current_user["id"])


@router.get("/lots", response_model=dict[UUID, list[FinderAmplifierLotResponse]])
async def get_available_finder_amplifier_lots(
    current_user: CurrentUser,
    service: Annotated[FinderAmplifierService, Depends(get_finder_amplifier_service)],
) -> dict[UUID, list[FinderAmplifierLotResponse]]:
    """Return available amplifier lots for the authenticated user, grouped by item ID."""

    inventory = await service.get_available_lots(user_id=current_user["id"])
    return {
        item_id: [
            FinderAmplifierLotResponse(
                id=lot.id,
                user_id=lot.user_id,
                type=lot.type.value,
                item=FinderAmplifierResponse.model_validate(amplifier),
                qty=lot.qty,
                reserved=lot.reserved,
                tier=lot.tool_lot.tier,
                tt=lot.tool_lot.tt,
                is_default=lot.tool_lot.is_default,
                created_at=lot.created_at,
                updated_at=lot.updated_at,
                is_active=lot.is_active,
            )
            for lot, amplifier in lots
        ]
        for item_id, lots in inventory.items()
    }


@router.get("/{item_id}", response_model=FinderAmplifierResponse)
async def get_finder_amplifier_by_id(
    item_id: UUID,
    service: Annotated[FinderAmplifierService, Depends(get_finder_amplifier_service)],
):
    amplifier = await service.get_by_id(item_id)
    if amplifier is None:
        raise AppError(status_code=404, message="Finder amplifier not found")
    return amplifier
