"""HTTP endpoints for excavator catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db import get_session
from api.db.repositories import ExcavatorRepository
from api.services import ExcavatorService

router = APIRouter(tags=["excavators"])


def get_excavator_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ExcavatorService:
    return ExcavatorService(ExcavatorRepository(session))


@router.get("")
async def get_all_excavators(
    service: Annotated[ExcavatorService, Depends(get_excavator_service)],
):
    return await service.get_all()


@router.get("/{item_id}")
async def get_excavator_by_id(
    item_id: UUID,
    service: Annotated[ExcavatorService, Depends(get_excavator_service)],
):
    excavator = await service.get_by_id(item_id)
    if excavator is None:
        raise AppError(status_code=404, message="Excavator not found")
    return excavator
