"""HTTP endpoints for refiner catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db import get_session
from api.db.repositories import RefinerRepository
from api.schemas import RefinerResponse
from api.services import RefinerService

router = APIRouter(tags=["refiners"])


def get_refiner_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RefinerService:
    return RefinerService(RefinerRepository(session))


@router.get("", response_model=list[RefinerResponse])
async def get_all_refiners(
    service: Annotated[RefinerService, Depends(get_refiner_service)],
):
    return await service.get_all()


@router.get("/{item_id}", response_model=RefinerResponse)
async def get_refiner_by_id(
    item_id: UUID,
    service: Annotated[RefinerService, Depends(get_refiner_service)],
):
    refiner = await service.get_by_id(item_id)
    if refiner is None:
        raise AppError(status_code=404, message="Refiner not found")
    return refiner
