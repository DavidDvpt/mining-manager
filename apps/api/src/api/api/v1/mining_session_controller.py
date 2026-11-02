"""HTTP endpoint for mining session creation."""

from collections.abc import Mapping
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.db import get_session
from api.db.models import Item, Lot
from api.schemas import (
    CreateMiningSessionRequest,
    CreateMiningSessionResponse,
    EnhancerDetailsResponse,
    ItemSummaryResponse,
    MiningEnhancerResponse,
    MiningSessionCostResponse,
    UnstackableLotResponse,
)
from api.services import MiningSessionCreation, get_session_mining_service

router = APIRouter(tags=["mining sessions"])


def _enhancer_lines(enhancers: Mapping[str, UUID]) -> list[UUID]:
    """Convert socket-keyed enhancer input into item-only line values."""

    return list(enhancers.values())


def _serialize_tool_lot(lot: Lot) -> UnstackableLotResponse:
    """Serialize an owned tool lot with its origin item summary."""

    if lot.origin is None or lot.origin.item is None or lot.tool_lot is None:
        raise RuntimeError("Created mining tool lot is missing its item details")
    return UnstackableLotResponse(
        id=lot.id,
        user_id=lot.user_id,
        type=lot.type.value,
        item=lot.origin.item,
        qty=lot.qty,
        reserved=lot.reserved,
        tier=lot.tool_lot.tier,
        tt=lot.tool_lot.tt,
        created_at=lot.created_at,
        updated_at=lot.updated_at,
        is_active=lot.is_active,
    )


def _serialize_enhancer(item: Item, stock: int) -> MiningEnhancerResponse:
    """Serialize an enhancer item with its socket, stock, and current usage."""

    if item.enhancer is None:
        raise RuntimeError("Created mining enhancer is missing catalog details")
    return MiningEnhancerResponse(
        socket=item.enhancer.socket,
        item=ItemSummaryResponse.model_validate(item),
        enhancer=EnhancerDetailsResponse.model_validate(item.enhancer),
        stock=stock,
        used=0,
    )


@router.post("/create", response_model=CreateMiningSessionResponse, status_code=201)
async def create_mining_session(
    payload: CreateMiningSessionRequest,
    current_user: CurrentUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> CreateMiningSessionResponse:
    """Create an owned mining session with validated cost lines."""

    creation: MiningSessionCreation = await get_session_mining_service(session).create(
        user_id=current_user["id"],
        clic=payload.clics,
        zone_id=payload.session_zone,
        search_type=payload.search_type,
        finders=payload.finder,
        excavators=payload.excavators,
        finder_amplifiers=payload.finder_amplifiers,
        finder_enhancers=_enhancer_lines(payload.finder_enhancers),
        excavator_enhancers=_enhancer_lines(payload.excavator_enhancers),
    )
    return CreateMiningSessionResponse(
        session_id=creation.session.id,
        finder=[_serialize_tool_lot(lot) for lot in creation.finders],
        excavators=[_serialize_tool_lot(lot) for lot in creation.excavators],
        finderAmplifiers=[
            _serialize_tool_lot(lot) for lot in creation.finder_amplifiers
        ],
        finderEnhancers=[
            _serialize_enhancer(item, stock)
            for item, stock in creation.enhancers[: len(payload.finder_enhancers)]
        ],
        excavatorEnhancers=[
            _serialize_enhancer(item, stock)
            for item, stock in creation.enhancers[len(payload.finder_enhancers) :]
        ],
        cost=MiningSessionCostResponse(
            tt=creation.total_tt,
            ttc=creation.total_ttc,
        ),
    )
