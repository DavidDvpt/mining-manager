"""Persistence operations for mining sessions and their cost lines."""

from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from api.db.models import (
    Session,
    SessionLine,
    SessionLineDecay,
    SessionLineType,
    SessionMining,
    SessionMiningSearchType,
    SessionZone,
    User,
    Lot,
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

    async def get_session_for_close(
        self, *, session_id: UUID, user_id: UUID
    ) -> Session | None:
        """Lock a user's mining session with all lines and lot details."""

        statement = (
            select(Session)
            .join(SessionMining, SessionMining.session_id == Session.id)
            .options(
                selectinload(Session.lines)
                .selectinload(SessionLine.lot)
                .selectinload(Lot.origin)
                .selectinload(SessionLine.item),
                selectinload(Session.lines)
                .selectinload(SessionLine.lot)
                .selectinload(Lot.tool_lot),
                selectinload(Session.lines).selectinload(SessionLine.decay),
            )
            .where(
                Session.id == session_id,
                Session.user_id == user_id,
            )
            .with_for_update()
        )
        return await self._session.scalar(statement)

    async def update_line_quantity(
        self, *, line: SessionLine, quantity: int, mode: str
    ) -> None:
        """Persist a line quantity under the database transition guard."""

        await self._session.execute(
            text(f"SET LOCAL app.session_line_update_mode = '{mode}'")
        )
        line.quantity = quantity
        await self._session.flush()

    async def update_session_line_decay(
        self, *, line: SessionLine, decay: Decimal
    ) -> None:
        """Create or update an excavator decay value for a session line."""

        if line.decay is None:
            line.decay = SessionLineDecay(decay_ttc=decay)
        else:
            line.decay.decay_ttc = decay
        await self._session.flush()

    async def close_session(self, *, session: Session) -> Session:
        """Set the session end date after all closing invariants are met."""

        session.ended_at = date.today()
        await self._session.flush()
        return session

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
            session_zone_id=zone_id,
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
