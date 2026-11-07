"""HTTP endpoints for lot management."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas import (
    ItemSummaryResponse,
    LotCollectionResponse,
    LotResponse,
    UnstackableLotResponse,
    UpdateUnstackableLotRequest,
)
from api.services import get_lot_service

router = APIRouter(tags=["lots"])


@router.get("/unstackable/{lot_id}", response_model=UnstackableLotResponse)
async def get_unstackable_lot(
    lot_id: UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnstackableLotResponse:
    """Return an owned unstackable lot with its item-specific attributes."""

    lot = await get_lot_service(session).get_unstackable_lot(
        user_id=current_user["id"],
        lot_id=lot_id,
    )
    origin = lot.origin
    if origin is None or origin.item is None:
        raise AppError(404, "Item not found")
    item = origin.item
    tool_lot = lot.tool_lot
    return UnstackableLotResponse(
        id=lot.id,
        user_id=lot.user_id,
        type=lot.type.value,
        item=ItemSummaryResponse.model_validate(item),
        qty=lot.qty,
        reserved=lot.reserved,
        tier=tool_lot.tier if tool_lot is not None else None,
        tt=tool_lot.tt if tool_lot is not None else None,
        is_default=getattr(tool_lot, "is_default", False),
        created_at=lot.created_at,
        updated_at=lot.updated_at,
        is_active=lot.is_active,
    )


@router.put("/unstackable/{lot_id}/default", response_model=UnstackableLotResponse)
async def set_default_tool_lot(
    lot_id: UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnstackableLotResponse:
    """Set an owned finder, excavator, or refiner lot as the user's default."""

    lot = await get_lot_service(session).set_default_tool_lot(
        user_id=current_user["id"], lot_id=lot_id
    )
    if lot.origin is None or lot.origin.item is None or lot.tool_lot is None:
        raise AppError(404, "Tool lot not found")
    return UnstackableLotResponse(
        id=lot.id,
        user_id=lot.user_id,
        type=lot.type.value,
        item=ItemSummaryResponse.model_validate(lot.origin.item),
        qty=lot.qty,
        reserved=lot.reserved,
        tier=lot.tool_lot.tier,
        tt=lot.tool_lot.tt,
        is_default=lot.tool_lot.is_default,
        created_at=lot.created_at,
        updated_at=lot.updated_at,
        is_active=lot.is_active,
    )


@router.put("/unstackable/{lot_id}", response_model=UnstackableLotResponse)
async def update_unstackable_lot(
    lot_id: UUID,
    payload: UpdateUnstackableLotRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> UnstackableLotResponse:
    """Update TT for a tool lot and tier for finder or excavator lots."""

    lot = await get_lot_service(session).update_unstackable_lot(
        user_id=current_user["id"],
        lot_id=lot_id,
        tier=payload.tier,
        tt=payload.tt,
    )
    if lot.origin is None or lot.origin.item is None or lot.tool_lot is None:
        raise AppError(404, "Tool lot not found")
    return UnstackableLotResponse(
        id=lot.id,
        user_id=lot.user_id,
        type=lot.type.value,
        item=ItemSummaryResponse.model_validate(lot.origin.item),
        qty=lot.qty,
        reserved=lot.reserved,
        tier=lot.tool_lot.tier,
        tt=lot.tool_lot.tt,
        is_default=lot.tool_lot.is_default,
        created_at=lot.created_at,
        updated_at=lot.updated_at,
        is_active=lot.is_active,
    )


@router.get("", response_model=LotCollectionResponse, include_in_schema=False)
@router.get("/{item_id}", response_model=LotCollectionResponse)
async def get_inventory_lots(
    item_id: UUID,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> LotCollectionResponse:
    """Return the connected user's active FIFO lots for a stackable item."""

    item, lots, total_quantity = await get_lot_service(session).get_fifo_lots(
        user_id=current_user["id"],
        item_id=item_id,
    )
    return LotCollectionResponse(
        item=ItemSummaryResponse.model_validate(item),
        lots=[LotResponse.model_validate(lot) for lot in lots],
        total_quantity=total_quantity,
    )
