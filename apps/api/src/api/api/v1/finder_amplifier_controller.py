"""HTTP endpoints for finder amplifier catalogue data."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db import get_session
from api.db.repositories import FinderAmplifierRepository
from api.services import FinderAmplifierService

router = APIRouter(tags=["finder-amplifiers"])


def get_finder_amplifier_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> FinderAmplifierService:
    return FinderAmplifierService(FinderAmplifierRepository(session))


@router.get("")
async def get_all_finder_amplifiers(
    service: Annotated[FinderAmplifierService, Depends(get_finder_amplifier_service)],
):
    return await service.get_all()


@router.get("/{item_id}")
async def get_finder_amplifier_by_id(
    item_id: UUID,
    service: Annotated[FinderAmplifierService, Depends(get_finder_amplifier_service)],
):
    amplifier = await service.get_by_id(item_id)
    if amplifier is None:
        raise AppError(status_code=404, message="Finder amplifier not found")
    return amplifier
