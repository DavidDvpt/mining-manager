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

        for item_id in enhancer_lines:
            mining_session.lines.append(
                SessionLine(
                    type=SessionLineType.CONSUMED,
                    item_id=item_id,
                    qty=0,
                )
            )

        self._session.add(mining_session)
        await self._session.flush()
        return mining_session
