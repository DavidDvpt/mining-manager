"""HTTP endpoints for lot management."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.db import get_session
from api.schemas import ItemSummaryResponse, LotCollectionResponse, LotResponse
from api.services import get_lot_service

router = APIRouter(tags=["lots"])


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
