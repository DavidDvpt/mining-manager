"""Business operations for planets and their zones."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError
from api.db.models import Planet, SessionZone
from api.db.repositories import PlanetRepository


class PlanetService:
    """Provide read-only planet queries and authenticated zone creation."""

    def __init__(self, repository: PlanetRepository) -> None:
        """Initialize the service with its dedicated planet repository."""

        self._repository = repository

    async def get_all(self) -> list[Planet]:
        """Return every planet in the catalogue."""

        return await self._repository.get_all()

    async def get_by_id(self, planet_id: UUID) -> Planet | None:
        """Return one planet by identifier."""

        return await self._repository.get_by_id(planet_id)

    async def get_zone(
        self, *, planet_id: UUID, zone_id: UUID, user_id: UUID
    ) -> SessionZone | None:
        """Return a user's zone only when its planet matches the route parameter."""

        return await self._repository.get_zone(
            planet_id=planet_id, zone_id=zone_id, user_id=user_id
        )

    async def get_zones_for_planet(
        self, *, planet_id: UUID, user_id: UUID
    ) -> list[SessionZone]:
        """Return all zones owned by the user for an existing planet."""

        if await self._repository.get_by_id(planet_id) is None:
            raise AppError(404, "Planet not found")
        return await self._repository.get_zones_for_planet(
            planet_id=planet_id, user_id=user_id
        )

    async def create_zone(
        self, *, planet_id: UUID, name: str, user_id: UUID
    ) -> SessionZone:
        """Create a zone owned by the authenticated user after validating its planet."""

        if user_id is None:
            raise AppError(401, "Unauthorized")
        if await self._repository.get_by_id(planet_id) is None:
            raise AppError(404, "Planet not found")
        return await self._repository.create_zone(
            planet_id=planet_id, name=name, user_id=user_id
        )


def get_planet_service(session: AsyncSession) -> PlanetService:
    """Build a planet service for the current database session."""

    return PlanetService(PlanetRepository(session))
