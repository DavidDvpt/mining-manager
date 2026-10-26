"""HTTP endpoint for the deposit size reference table."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.db import get_session
from api.db.models import DepositSize
from api.db.repositories import DepositSizeRepository
from api.schemas import DepositSizeResponse
from api.services import DepositSizeService

router = APIRouter(tags=["deposit-sizes"])


def get_deposit_size_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> DepositSizeService:
    return DepositSizeService(DepositSizeRepository(session))


@router.get("/deposit_sizes", response_model=list[DepositSizeResponse])
async def get_all(
    service: Annotated[
        DepositSizeService,
        Depends(get_deposit_size_service),
    ],
) -> list[DepositSize]:
    return await service.get_all()
