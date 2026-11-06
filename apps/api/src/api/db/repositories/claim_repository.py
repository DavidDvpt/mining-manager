"""Persistence operations for mining claims."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from api.db.models import Claim, Item, Session


class ClaimRepository:
    """Load and persist claims while enforcing the owning user scope."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize the repository with the request-scoped database session."""

        self._session = session

    @property
    def session(self) -> AsyncSession:
        """Return the database session used by this repository."""

        return self._session

    def _query(self):
        """Build a claim query with the item and its economy value eagerly loaded."""

        return (
            select(Claim)
            .join(Session, Session.id == Claim.session_id)
            .options(joinedload(Claim.item).joinedload(Item.economy))
        )

    async def get_all_for_user(
        self, *, session_id: UUID, user_id: UUID
    ) -> list[Claim]:
        """Return all claims for an owned mining session in creation order."""

        result = await self._session.scalars(
            self._query()
            .where(Claim.session_id == session_id, Session.user_id == user_id)
            .order_by(Claim.created_at, Claim.id)
        )
        return list(result.all())

    async def get_for_user(
        self, *, claim_id: UUID, session_id: UUID, user_id: UUID
    ) -> Claim | None:
        """Return one claim when both its session and user ownership match."""

        return await self._session.scalar(
            self._query().where(
                Claim.id == claim_id,
                Claim.session_id == session_id,
                Session.user_id == user_id,
            )
        )

    async def create(
        self,
        *,
        session_id: UUID,
        item_id: UUID,
        qty: int,
        is_hof: bool,
        depth: Decimal | None,
        latitude: int | None,
        longitude: int | None,
        depleted: bool,
    ) -> Claim:
        """Persist a claim and return it after its database identifier is assigned."""

        claim = Claim(
            session_id=session_id,
            item_id=item_id,
            qty=qty,
            is_hof=is_hof,
            depth=depth,
            latitude=latitude,
            longitude=longitude,
            depleted=depleted,
        )
        self._session.add(claim)
        await self._session.flush()
        return claim

    async def update(self, *, claim: Claim, values: dict[str, object]) -> Claim:
        """Apply validated mutable fields to a claim and flush the changes."""

        for field, value in values.items():
            setattr(claim, field, value)
        await self._session.flush()
        return claim
