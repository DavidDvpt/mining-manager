"""HTTP endpoints for material catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db import get_session
from api.db.repositories import MaterialRepository
from api.services import MaterialService

router = APIRouter(tags=["materials"])


def get_material_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MaterialService:
    return MaterialService(MaterialRepository(session))


@router.get("")
async def get_all_materials(
    service: Annotated[MaterialService, Depends(get_material_service)],
):
    return await service.get_all()


@router.get("/{item_id}")
async def get_material_by_id(
    item_id: UUID,
    service: Annotated[MaterialService, Depends(get_material_service)],
):
    material = await service.get_by_id(item_id)
    if material is None:
        raise AppError(status_code=404, message="Material not found")
    return material
