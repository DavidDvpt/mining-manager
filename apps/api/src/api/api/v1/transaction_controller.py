"""HTTP endpoints for named transaction sessions."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.db import get_session
from api.db.models import SessionTransactionTypeDetail
from api.schemas import (
    CreateStackableBuyRequest,
    CreateUnstackableBuyRequest,
    SessionTransactionResponse,
)
from api.services import get_session_transaction_service

router = APIRouter(tags=["transactions"])


@router.post("/buy/stackable", response_model=SessionTransactionResponse, status_code=201)
async def create_buy_stackable(
    payload: CreateStackableBuyRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionTransactionResponse:
    """Create a BUY session for a stackable item."""

    transaction_session = await get_session_transaction_service(session).create_buy_stackable(
        user_id=current_user["id"],
        quantity=payload.quantity,
        kind=payload.kind,
        type_detail=SessionTransactionTypeDetail(payload.type_detail),
        item_id=payload.item_id,
        fee=payload.fee,
        ttc=payload.ttc,
    )
    transaction = transaction_session.transaction
    return SessionTransactionResponse(
        session_id=transaction_session.id,
        type=transaction.type.value,
        status=transaction.status.value,
    )


@router.post("/buy/unstackable", response_model=SessionTransactionResponse, status_code=201)
async def create_buy_unstackable(
    payload: CreateUnstackableBuyRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionTransactionResponse:
    """Create a BUY session for one non-stackable lot."""

    transaction_session = await get_session_transaction_service(session).create_buy_unstackable(
        user_id=current_user["id"],
        item_id=payload.item_id,
        tt=payload.tt,
        kind=payload.kind,
        type_detail=SessionTransactionTypeDetail(payload.type_detail),
        fee=payload.fee,
        ttc=payload.ttc,
    )
    transaction = transaction_session.transaction
    return SessionTransactionResponse(
        session_id=transaction_session.id,
        type=transaction.type.value,
        status=transaction.status.value,
    )
