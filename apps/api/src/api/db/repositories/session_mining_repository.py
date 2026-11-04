"""Persistence operations for mining sessions and their cost lines."""

from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.db.models import (
    Session,
    SessionLine,
    SessionLineDecay,
    SessionLineType,
    SessionMining,
    SessionMiningSearchType,
    SessionZone,
    User,
)


class SessionMiningRepository:
    """Persist and load the inventory data used by mining sessions."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_zone(self, *, zone_id: UUID) -> SessionZone | None:
        """Return a session zone by id, or ``None`` when it does not exist."""

        return await self._session.scalar(
            select(SessionZone).where(SessionZone.id == zone_id)
        )

    async def lock_user(self, *, user_id: UUID) -> None:
        """Lock an existing user row for serialized session creation."""

        await self._session.scalar(
            select(User).where(User.id == user_id).with_for_update()
        )

    async def get_open_session(self, *, user_id: UUID) -> Session | None:
        """Return the user's open mining session, if one exists."""

        return await self._session.scalar(
            select(Session)
            .join(SessionMining, SessionMining.session_id == Session.id)
            .where(Session.user_id == user_id, Session.ended_at.is_(None))
        )

    async def create(
        self,
        *,
        user_id: UUID,
        clic: int,
        zone_id: UUID | None,
        search_type: SessionMiningSearchType,
        tool_lines: list[dict[str, object]],
        enhancer_lines: list[UUID],
    ) -> Session:
        """Persist a mining session and its validated cost lines atomically."""

        mining_session = Session(user_id=user_id)
        mining_session.mining = SessionMining(
            clic=clic,
            session_sone_id=zone_id,
            search_type=search_type,
        )

        for values in tool_lines:
            line = SessionLine(
                type=SessionLineType.CONSUMED,
                lot_id=values["lot_id"],
            )
            decay = values.get("decay")
            if isinstance(decay, Decimal):
                line.decay = SessionLineDecay(decay_ttc=decay)
            mining_session.lines.append(line)

        self._session.add(mining_session)
        await self._session.flush()
        return mining_session
