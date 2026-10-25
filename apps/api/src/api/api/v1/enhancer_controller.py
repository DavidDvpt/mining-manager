"""HTTP endpoints for enhancer catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db import get_session
from api.db.repositories import EnhancerRepository
from api.schemas import EnhancerResponse
from api.services import EnhancerService

router = APIRouter(tags=["enhancers"])


def get_enhancer_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> EnhancerService:
    return EnhancerService(EnhancerRepository(session))


@router.get("", response_model=list[EnhancerResponse])
async def get_all_enhancers(
    service: Annotated[EnhancerService, Depends(get_enhancer_service)],
):
    return await service.get_all()


@router.get("/{item_id}", response_model=EnhancerResponse)
async def get_enhancer_by_id(
    item_id: UUID,
    service: Annotated[EnhancerService, Depends(get_enhancer_service)],
):
    enhancer = await service.get_by_id(item_id)
    if enhancer is None:
        raise AppError(status_code=404, message="Enhancer not found")
    return enhancer
