"""HTTP endpoints for finder catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas import FinderResponse
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
