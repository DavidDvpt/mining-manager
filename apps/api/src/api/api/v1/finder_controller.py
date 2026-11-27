"""HTTP endpoints for finder catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas import FinderResponse
from api.schemas.finder_schema import FinderLotResponse
from api.services import FinderService
from api.services import get_finder_service as build_finder_service

router = APIRouter(tags=["finders"])


def get_finder_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FinderService:
    """Build the finder service for the current request."""

    return build_finder_service(session)


@router.get("", response_model=list[FinderResponse])
async def get_all_finders(
    service: Annotated[FinderService, Depends(get_finder_service)],
):
    """Return all finders from the catalogue."""

    return await service.get_all()


@router.get("/stock", response_model=dict[UUID, int])
async def get_finder_stock(
    current_user: CurrentUser,
    service: Annotated[FinderService, Depends(get_finder_service)],
) -> dict[UUID, int]:
    """Return available finder stock grouped by catalogue item ID."""

    return await service.get_stock(user_id=current_user["id"])


@router.get("/lots", response_model=dict[UUID, list[FinderLotResponse]])
async def get_available_finder_lots(
    current_user: CurrentUser,
    service: Annotated[FinderService, Depends(get_finder_service)],
) -> dict[UUID, list[FinderLotResponse]]:
    """Return available finder lots for the authenticated user, grouped by item ID."""

    inventory = await service.get_available_lots(user_id=current_user["id"])
    return {
        item_id: [
            FinderLotResponse(
                id=lot.id,
                user_id=lot.user_id,
                type=lot.type.value,
                item=FinderResponse.model_validate(finder),
                qty=lot.qty,
                reserved=lot.reserved,
                tier=lot.tool_lot.tier,
                tt=lot.tool_lot.tt,
                is_default=lot.tool_lot.is_default,
                created_at=lot.created_at,
                updated_at=lot.updated_at,
                is_active=lot.is_active,
            )
            for lot, finder in lots
        ]
        for item_id, lots in inventory.items()
    }


@router.get("/{item_id}", response_model=FinderResponse)
async def get_finder_by_id(
    item_id: UUID,
    service: Annotated[FinderService, Depends(get_finder_service)],
):
    """Return one finder from the catalogue."""

    finder = await service.get_by_id(item_id)
    if finder is None:
        raise AppError(status_code=404, message="Finder not found")
    return finder
