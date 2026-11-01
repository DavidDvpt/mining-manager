"""HTTP endpoints for named transaction sessions."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.db import get_session
from api.db.models import SessionTransactionStatus, SessionTransactionTypeDetail
from api.schemas import (
    CreateStackableBuyRequest,
    CreateConsumedMaterialRequest,
    CreateStackableSellRequest,
    CreateUnstackableBuyRequest,
    CreateUnstackableSellRequest,
    SessionTransactionResponse,
    UpdateTransactionStatusRequest,
)
from api.services import get_session_transaction_service

router = APIRouter(tags=["transactions"])


@router.post("/consumed/material", response_model=SessionTransactionResponse, status_code=201)
async def create_consumed_material(
    payload: CreateConsumedMaterialRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionTransactionResponse:
    """Consume owned material stock for vehicle fuel or another resource use."""

    transaction_session = await get_session_transaction_service(session).create_consumed_material(
        user_id=current_user["id"],
        item_id=payload.item_id,
        quantity=payload.quantity,
    )
    transaction = transaction_session.transaction
    if transaction is None:
        raise RuntimeError("Created transaction session has no transaction")
    return SessionTransactionResponse(
        session_id=transaction_session.id,
        type=transaction.type.value,
        status=transaction.status.value,
    )


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
    if transaction is None:
        raise RuntimeError("Created transaction session has no transaction")
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
    if transaction is None:
        raise RuntimeError("Created transaction session has no transaction")
    return SessionTransactionResponse(
        session_id=transaction_session.id,
        type=transaction.type.value,
        status=transaction.status.value,
    )


@router.post("/sell/stackable", response_model=SessionTransactionResponse, status_code=201)
async def create_sell_stackable(
    payload: CreateStackableSellRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionTransactionResponse:
    """Create a SELL session for a stackable item."""

    transaction_session = await get_session_transaction_service(session).create_sell_stackable(
        user_id=current_user["id"],
        item_id=payload.item_id,
        quantity=payload.quantity,
        tt=payload.tt,
        ttc=payload.ttc,
    )
    transaction = transaction_session.transaction
    if transaction is None:
        raise RuntimeError("Created transaction session has no transaction")
    return SessionTransactionResponse(
        session_id=transaction_session.id,
        type=transaction.type.value,
        status=transaction.status.value,
    )


@router.post("/sell/unstackable", response_model=SessionTransactionResponse, status_code=201)
async def create_sell_unstackable(
    payload: CreateUnstackableSellRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionTransactionResponse:
    """Create a SELL session for one owned unstackable lot."""

    transaction_session = await get_session_transaction_service(session).create_sell_unstackable(
        user_id=current_user["id"],
        lot_id=payload.lot_id,
        tt=payload.tt,
        ttc=payload.ttc,
    )
    transaction = transaction_session.transaction
    if transaction is None:
        raise RuntimeError("Created transaction session has no transaction")
    return SessionTransactionResponse(
        session_id=transaction_session.id,
        type=transaction.type.value,
        status=transaction.status.value,
    )


@router.patch("/{session_id}/status", response_model=SessionTransactionResponse)
async def update_transaction_status(
    session_id: UUID,
    payload: UpdateTransactionStatusRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> SessionTransactionResponse:
    """Set the status of an owned running SELL transaction session."""

    transaction = await get_session_transaction_service(session).patch_status(
        user_id=current_user["id"],
        session_id=session_id,
        status=SessionTransactionStatus(payload.status),
    )
    return SessionTransactionResponse(
        session_id=transaction.session_id,
        type=transaction.type.value,
        status=transaction.status.value,
    )
