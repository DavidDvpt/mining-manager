"""HTTP endpoints for material type catalogue data."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_session
from api.db.repositories import MaterialTypeRepository
from api.schemas import MaterialTypeResponse
from api.services import MaterialTypeService

router = APIRouter(tags=["material-types"])


def get_material_type_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> MaterialTypeService:
    """Build the material type service from the current database session."""

    return MaterialTypeService(MaterialTypeRepository(session))


@router.get("", response_model=list[MaterialTypeResponse])
async def get_all_material_types(
    service: Annotated[MaterialTypeService, Depends(get_material_type_service)],
) -> list[MaterialTypeResponse]:
    """Return active material types ordered by display name."""

    material_types = await service.get_all()
    return [
        MaterialTypeResponse.model_validate(material_type)
        for material_type in material_types
    ]
