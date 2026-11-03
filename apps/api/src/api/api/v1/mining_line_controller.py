"""HTTP endpoints for produced lines in mining sessions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.db import get_session
from api.schemas import (
    CreateProducedSessionLineRequest,
    SessionLineResponse,
    UpdateProducedSessionLineRequest,
)
from api.services import get_session_line_service

router = APIRouter(tags=["mining session lines"])


@router.post(
    "/{session_id}/lines/",
    response_model=SessionLineResponse,
    status_code=201,
)
async def create_produced_session_line(
    session_id: UUID,
    payload: CreateProducedSessionLineRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionLineResponse:
    """Create a produced line for an owned open mining session."""

    line = await get_session_line_service(session).create_produced_line(
        session_id=session_id,
        item_id=payload.item_id,
        quantity=payload.quantity,
        user_id=current_user["id"],
    )
    return SessionLineResponse.model_validate(line)


@router.put(
    "/{session_id}/lines/{session_line_id}",
    response_model=SessionLineResponse,
)
async def update_produced_session_line(
    session_id: UUID,
    session_line_id: UUID,
    payload: UpdateProducedSessionLineRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionLineResponse:
    """Replace only the quantity of an owned produced mining line."""

    line = await get_session_line_service(session).update_produced_line_quantity(
        session_id=session_id,
        session_line_id=session_line_id,
        quantity=payload.quantity,
        user_id=current_user["id"],
    )
    return SessionLineResponse.model_validate(line)


@router.delete("/{session_id}/lines/{session_line_id}", status_code=204)
async def delete_produced_session_line(
    session_id: UUID,
    session_line_id: UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> None:
    """Delete a produced line that has not generated an inventory lot."""

    await get_session_line_service(session).delete_produced_line(
        session_id=session_id,
        session_line_id=session_line_id,
        user_id=current_user["id"],
    )
