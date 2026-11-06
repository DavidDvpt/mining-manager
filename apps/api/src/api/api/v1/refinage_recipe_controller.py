"""HTTP endpoints for refinage recipe catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_session
from api.db.repositories import RefinageRecipeRepository
from api.schemas import RefinageRecipeResponse
from api.services.refinage_recipe_service import RefinageRecipeService

router = APIRouter(tags=["refinage"])


def get_refinage_recipe_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> RefinageRecipeService:
    """Build the refinage recipe service for the current database session."""

    return RefinageRecipeService(RefinageRecipeRepository(session))


@router.get("/recipe/{origin_id}", response_model=list[RefinageRecipeResponse])
async def get_recipes_by_origin(
    origin_id: UUID,
    service: Annotated[RefinageRecipeService, Depends(get_refinage_recipe_service)],
):
    """Return all refinage recipes consuming the requested origin material."""

    return await service.get_by_origin(origin_id)
