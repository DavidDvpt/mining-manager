"""HTTP endpoints for claims belonging to mining sessions."""

from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.db import get_session
from api.schemas import (
    ClaimCollectionResponse,
    ClaimRequest,
    ClaimResponse,
    ClaimResultResponse,
    CreateClaimRequest,
)
from api.services import ClaimService
from api.services import get_claim_service as build_claim_service
from api.services.claim_service import ClaimCreateValues

router = APIRouter(tags=["claims"])


def get_claim_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ClaimService:
    """Build the claim service for the current request-scoped session."""

    return build_claim_service(session)


@router.get("/{session_id}/claims", response_model=ClaimCollectionResponse)
async def get_all_claims(
    session_id: UUID,
    current_user: CurrentUser,
    service: Annotated[ClaimService, Depends(get_claim_service)],
) -> ClaimCollectionResponse:
    """Return claims and totals grouped by item for the user's mining session."""

    claims, result = await service.get_all(
        session_id=session_id, user_id=current_user["id"]
    )
    return ClaimCollectionResponse(
        claims=[ClaimResponse.model_validate(claim) for claim in claims],
        result=[ClaimResultResponse.model_validate(item) for item in result],
    )


@router.post(
    "/{session_id}/claims",
    response_model=ClaimResponse,
    status_code=201,
)
async def create_claim(
    session_id: UUID,
    payload: CreateClaimRequest,
    current_user: CurrentUser,
    service: Annotated[ClaimService, Depends(get_claim_service)],
) -> ClaimResponse:
    """Create and serialize a claim for the authenticated user's session."""

    claim = await service.create(
        session_id=session_id,
        user_id=current_user["id"],
        values=cast(ClaimCreateValues, payload.model_dump()),
    )
    return ClaimResponse.model_validate(claim)


@router.patch(
    "/{session_id}/claims/{claim_id}",
    response_model=ClaimResponse,
)
@router.put(
    "/{session_id}/claims/{claim_id}",
    response_model=ClaimResponse,
)
async def update_claim(
    session_id: UUID,
    claim_id: UUID,
    payload: ClaimRequest,
    current_user: CurrentUser,
    service: Annotated[ClaimService, Depends(get_claim_service)],
) -> ClaimResponse:
    """Update supplied claim fields and serialize the recalculated claim."""

    claim = await service.update(
        claim_id=claim_id,
        session_id=session_id,
        user_id=current_user["id"],
        values=payload.model_dump(exclude_unset=True),
    )
    return ClaimResponse.model_validate(claim)
