"""HTTP endpoints for the authenticated user's profile."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas.auth_schema import ProfileResponse
from api.services.profile_service import get_profile

router = APIRouter(tags=["profile"])
DbSession = Annotated[AsyncSession, Depends(get_session)]


@router.get("", response_model=ProfileResponse)
async def profile(current_user: CurrentUser, session: DbSession) -> dict:
    result = await get_profile(session, current_user["id"])
    if result is None:
        raise AppError(404, "Profile not found")
    return result
