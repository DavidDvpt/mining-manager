"""HTTP endpoints for finder catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db import get_session
from api.db.repositories import FinderRepository
from api.schemas import FinderResponse
from api.services import FinderService

router = APIRouter(tags=["finders"])


def get_finder_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FinderService:
    """Build the finder service for the current request."""

    return FinderService(FinderRepository(session))


@router.get("", response_model=list[FinderResponse])
async def get_all_finders(
    service: Annotated[FinderService, Depends(get_finder_service)],
):
    """Return all finders from the catalogue."""

    return await service.get_all()


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
