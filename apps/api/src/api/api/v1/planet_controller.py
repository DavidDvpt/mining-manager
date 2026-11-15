"""HTTP endpoints for planets and their zones."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.api.deps import CurrentUser
from api.core.exceptions import AppError
from api.db import get_session
from api.schemas import CreateZoneRequest, PlanetResponse, ZoneResponse
from api.services import PlanetService
from api.services.planet_service import get_planet_service as build_planet_service

router = APIRouter(tags=["planets"])


def get_planet_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> PlanetService:
    """Build the planet service for the current request-scoped session."""

    return build_planet_service(session)


@router.get("", response_model=list[PlanetResponse])
async def get_all_planets(
    service: Annotated[PlanetService, Depends(get_planet_service)],
) -> list[PlanetResponse]:
    """Return every planet in the catalogue."""

    planets = await service.get_all()
    return [PlanetResponse.model_validate(planet) for planet in planets]


@router.get("/{planet_id}", response_model=PlanetResponse)
async def get_planet(
    planet_id: UUID,
    service: Annotated[PlanetService, Depends(get_planet_service)],
) -> PlanetResponse:
    """Return one planet or a not-found error."""

    planet = await service.get_by_id(planet_id)
    if planet is None:
        raise AppError(404, "Planet not found")
    return PlanetResponse.model_validate(planet)


@router.get("/{planet_id}/zone", response_model=list[ZoneResponse])
async def get_planet_zones(
    planet_id: UUID,
    current_user: CurrentUser,
    service: Annotated[PlanetService, Depends(get_planet_service)],
) -> list[ZoneResponse]:
    """Return all zones belonging to one planet."""

    zones = await service.get_zones_for_planet(
        planet_id=planet_id, user_id=current_user["id"]
    )
    return [ZoneResponse.model_validate(zone) for zone in zones]


@router.get("/{planet_id}/zone/{zone_id}", response_model=ZoneResponse)
async def get_planet_zone(
    planet_id: UUID,
    zone_id: UUID,
    current_user: CurrentUser,
    service: Annotated[PlanetService, Depends(get_planet_service)],
) -> ZoneResponse:
    """Return one zone when it belongs to the requested planet."""

    zone = await service.get_zone(
        planet_id=planet_id, zone_id=zone_id, user_id=current_user["id"]
    )
    if zone is None:
        raise AppError(404, "Zone not found")
    return ZoneResponse.model_validate(zone)


@router.post("/{planet_id}/zone", response_model=ZoneResponse, status_code=201)
async def create_planet_zone(
    planet_id: UUID,
    payload: CreateZoneRequest,
    current_user: CurrentUser,
    service: Annotated[PlanetService, Depends(get_planet_service)],
) -> ZoneResponse:
    """Create a zone for an existing planet on behalf of the authenticated user."""

    zone = await service.create_zone(
        planet_id=planet_id,
        name=payload.name,
        user_id=current_user["id"],
    )
    return ZoneResponse.model_validate(zone)
