"""Persistence operations for planets and their zones."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import Planet, SessionZone


class PlanetRepository:
    """Load planets and persist zones owned by the planet catalogue domain."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the request-scoped database session."""

        self._session = session

    async def get_all(self) -> list[Planet]:
        """Return all planets ordered by name."""

        result = await self._session.scalars(select(Planet).order_by(Planet.name))
        return list(result.all())

    async def get_by_id(self, planet_id: UUID) -> Planet | None:
        """Return one planet by identifier, or ``None`` when it does not exist."""

        return await self._session.scalar(select(Planet).where(Planet.id == planet_id))

    async def get_zone(
        self, *, planet_id: UUID, zone_id: UUID, user_id: UUID
    ) -> SessionZone | None:
        """Return a user's zone only when it belongs to the requested planet."""

        return await self._session.scalar(
            select(SessionZone).where(
                SessionZone.id == zone_id,
                SessionZone.planete_id == planet_id,
                SessionZone.user_id == user_id,
            )
        )

    async def get_zones_for_planet(
        self, *, planet_id: UUID, user_id: UUID
    ) -> list[SessionZone]:
        """Return the user's zones belonging to one planet ordered by name."""

        result = await self._session.scalars(
            select(SessionZone)
            .where(
                SessionZone.planete_id == planet_id,
                SessionZone.user_id == user_id,
            )
            .order_by(SessionZone.name)
        )
        return list(result.all())

    async def create_zone(
        self, *, planet_id: UUID, name: str, user_id: UUID
    ) -> SessionZone:
        """Persist a user's zone and flush its generated identifier."""

        zone = SessionZone(name=name, planete_id=planet_id, user_id=user_id)
        self._session.add(zone)
        await self._session.flush()
        return zone
