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
