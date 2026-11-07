"""HTTP endpoints for authenticated user storage."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.db import get_session
from api.services import StorageService, get_storage_service

router = APIRouter(tags=["storage"])


def storage_service_dependency(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> StorageService:
    """Build the storage service dependency from the current DB session."""

    return get_storage_service(session)


@router.get("/material/stock", response_model=dict[UUID, int])
async def get_material_stock(
    current_user: CurrentUser,
    service: Annotated[StorageService, Depends(storage_service_dependency)],
) -> dict[UUID, int]:
    """Return available material stock grouped by material catalogue ID."""

    return await service.get_material_stock(user_id=current_user["id"])


@router.get("/material/{material_id}/stock", response_model=dict[UUID, int])
async def get_material_stock_for_item(
    material_id: UUID,
    current_user: CurrentUser,
    service: Annotated[StorageService, Depends(storage_service_dependency)],
) -> dict[UUID, int]:
    """Return available stock for one material catalogue item."""

    return await service.get_material_stock_for_item(
        user_id=current_user["id"],
        material_id=material_id,
    )
