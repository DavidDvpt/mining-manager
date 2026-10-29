"""HTTP endpoints for lot management."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.db import get_session
from api.schemas import LotCreateRequest, LotIdResponse
from api.services import create_lot

router = APIRouter(tags=["lots"])


@router.post("", response_model=LotIdResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_lot(
    body: LotCreateRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LotIdResponse:
    """Create a lot owned by the authenticated user and return its id."""

    lot = await create_lot(
        session,
        user_id=current_user["id"],
        kind=body.kind,
        session_line_id=body.session_line_id,
        quantity=body.quantity,
        tt=body.tt,
    )
    return LotIdResponse(id=lot.id)
