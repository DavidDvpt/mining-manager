"""Business operations for mining session creation."""

from collections.abc import Mapping
from contextlib import asynccontextmanager
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import (
    Item,
    Lot,
    LotKind,
    Session,
    SessionLine,
    SessionLineType,
    SessionMiningSearchType,
)
from api.db.repositories import SessionMiningRepository

from .enhancer_service import EnhancerService, get_enhancer_service
from .item_service import is_limited_item
from .lot_service import LotService, get_lot_service


@dataclass(frozen=True)
class MiningSessionCreation:
    """Data required to serialize a newly created mining session."""

    session: Session
    finders: list[Lot]
    excavators: list[Lot]
    finder_amplifiers: list[Lot]
    enhancers: list[tuple[Item, int]]
    total_tt: Decimal
    total_ttc: Decimal


@asynccontextmanager
async def _transaction_scope(session: AsyncSession):
    """Open a transaction or savepoint for the supplied database session."""

    transaction = session.begin_nested() if session.in_transaction() else session.begin()
    async with transaction:
        yield


class SessionMiningService:
    """Validate owned mining equipment and create mining sessions."""

    def __init__(
        self,
        session: AsyncSession,
        repository: SessionMiningRepository,
        lot_service: LotService,
        enhancer_service: EnhancerService,
    ) -> None:
        self._session = session
        self._repository = repository
        self._lot_service = lot_service
        self._enhancer_service = enhancer_service

    async def create(
        self,
        *,
        user_id: UUID,
        clic: int,
        zone_id: UUID | None,
        search_type: SessionMiningSearchType,
        finders: list[UUID],
        excavators: list[UUID],
        finder_amplifiers: list[UUID],
        finder_enhancers: list[UUID],
        excavator_enhancers: list[UUID],
    ) -> MiningSessionCreation:
        """Create a mining session and calculate its initial cost summary."""

        if clic < 1:
            raise UnprocessingError("clic must be greater than zero")
        multiplier = Decimal(len(search_type.value))

        async with _transaction_scope(self._session):
            await self._repository.lock_user(user_id=user_id)
            if await self._repository.get_open_session(user_id=user_id) is not None:
                raise UnprocessingError("A mining session is already open")
            if zone_id is not None and await self._repository.get_zone(zone_id=zone_id) is None:
                raise AppError(404, "Session zone not found")

            finder_lots = [
                await self._required_tool(user_id=user_id, lot_id=lot_id, role="finder")
                for lot_id in finders
            ]
            self._validate_identical_finders(finder_lots)
            self._validate_limited_tool_capacity(
                finder_lots, role="finder", clic=clic, multiplier=multiplier
            )

            excavator_lots = [
                await self._required_tool(
                    user_id=user_id, lot_id=lot_id, role="excavator"
                )
                for lot_id in excavators
            ]
            self._validate_limited_tool_capacity(
                excavator_lots,
                role="excavator",
                clic=clic,
                multiplier=multiplier,
            )
            amplifier_lots = [
                await self._required_tool(
                    user_id=user_id, lot_id=lot_id, role="finder amplifier"
                )
                for lot_id in finder_amplifiers
            ]
            if amplifier_lots:
                self._validate_amplifier_capacity(
                    amplifier_lots, clic=clic, multiplier=multiplier
                )

            tool_lines: list[dict[str, object]] = []
            tool_lines.extend(
                self._tool_line(lot, clic, multiplier, is_finder=True)
                for lot in finder_lots
            )
            tool_lines.extend(
                self._tool_line(lot, clic, multiplier)
                for lot in excavator_lots
            )
            tool_lines.extend(
                self._tool_line(lot, clic, multiplier)
                for lot in amplifier_lots
            )
            enhancer_lines = finder_enhancers + excavator_enhancers
            session = await self._repository.create(
                user_id=user_id,
                clic=clic,
                zone_id=zone_id,
                search_type=search_type,
                tool_lines=tool_lines,
                enhancer_lines=enhancer_lines,
            )
            enhancer_data = []
            for item_id in enhancer_lines:
                item, _lots, _stock = await self._lot_service.get_fifo_lots(
                    user_id=user_id,
                    item_id=item_id,
                )
                if item.enhancer is None:
                    raise AppError(404, "Enhancer item not found")
                max_stock = await self._enhancer_service.get_stock_by_type_socket(
                    user_id=user_id,
                    enhancer_type=item.enhancer.type.value,
                    socket=item.enhancer.socket,
                )
                enhancer_data.append((item, max_stock))

            total_tt, total_ttc = self._calculate_costs(
                finder_lots=finder_lots,
                amplifier_lots=amplifier_lots,
                clic=clic,
                multiplier=multiplier,
            )
            return MiningSessionCreation(
                session=session,
                finders=finder_lots,
                excavators=excavator_lots,
                finder_amplifiers=amplifier_lots,
                enhancers=enhancer_data,
                total_tt=total_tt,
                total_ttc=total_ttc,
            )

    async def close(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        tool_decays: dict[UUID, Decimal],
        amplifier_tts: dict[UUID, Decimal],
        enhancer_quantities: dict[UUID, int],
        produced_quantities: dict[UUID, int],
    ) -> Session:
        """Close a mining session after confirming every final line value.

        Every excavator line must have a decay entry, enhancer quantities are
        finalized from the payload, produced quantities are reconciled, and a
        transaction lot is created for every produced line before the session
        is marked closed.
        """

        async with _transaction_scope(self._session):
            mining_session = await self._repository.get_session_for_close(
                session_id=session_id, user_id=user_id
            )
            if mining_session is None:
                raise AppError(404, "Mining session not found")
            if mining_session.ended_at is not None:
                raise UnprocessingError("The mining session is already closed")

            lines = mining_session.lines
            tool_lines: list[SessionLine] = []
            for line in lines:
                item = self._line_item(line)
                if (
                    line.type is SessionLineType.CONSUMED
                    and item is not None
                    and (
                        item.finder is not None
                        or item.excavator is not None
                        or item.finder_amplifier is not None
                    )
                ):
                    tool_lines.append(line)
            self._require_exact_keys(
                tool_decays,
                {line.id for line in tool_lines},
                "tool decays",
            )
            for line in tool_lines:
                await self._repository.update_session_line_decay(
                    line=line, decay=tool_decays[line.id]
                )

            amplifier_lines: list[SessionLine] = []
            for line in tool_lines:
                item = self._line_item(line)
                if item is not None and item.finder_amplifier is not None:
                    amplifier_lines.append(line)
            self._require_exact_keys(
                amplifier_tts,
                {line.id for line in amplifier_lines},
                "amplifier TT values",
            )
            for line in amplifier_lines:
                lot = line.lot
                if lot is None or lot.tool_lot is None:
                    raise UnprocessingError("Amplifier line has no tool lot")
                lot.tool_lot.tt = amplifier_tts[line.id]

            enhancer_lines: list[SessionLine] = []
            for line in lines:
                item = self._line_item(line)
                if (
                    line.type is SessionLineType.CONSUMED
                    and item is not None
                    and item.enhancer is not None
                ):
                    enhancer_lines.append(line)
            self._require_exact_keys(
                enhancer_quantities,
                {line.id for line in enhancer_lines},
                "enhancer quantities",
            )
            await self._set_final_quantities(
                enhancer_lines, enhancer_quantities, mode="close"
            )

            produced_lines = [
                line for line in lines if line.type is SessionLineType.PRODUCED
            ]
            self._require_exact_keys(
                produced_quantities,
                {line.id for line in produced_lines},
                "produced quantities",
            )
            for line in produced_lines:
                quantity = produced_quantities[line.id]
                if quantity < 0:
                    raise UnprocessingError("Produced quantity cannot be negative")
                if line.qty != quantity:
                    await self._repository.update_line_quantity(
                        line=line, quantity=quantity, mode="produced_qty"
                    )
                await self._lot_service.create_lot(
                    user_id=user_id,
                    kind=LotKind.MATERIAL,
                    session_line_id=line.id,
                    quantity=quantity,
                    tt=None,
                )

            return await self._repository.close_session(session=mining_session)

    @staticmethod
    def _require_exact_keys(
        values: Mapping[UUID, object], expected: set[UUID], label: str
    ) -> None:
        """Require a finalization mapping to mention each and only each line."""

        if set(values) != expected:
            raise UnprocessingError(f"The payload must contain all {label}")

    @staticmethod
    def _line_item(line: SessionLine) -> Item | None:
        """Return a session line's item when its lot and origin are present."""

        if line.lot is None or line.lot.origin is None:
            return None
        return line.lot.origin.item

    async def _set_final_quantities(
        self,
        lines: list,
        quantities: dict[UUID, int],
        *,
        mode: str,
    ) -> None:
        """Apply final quantities to a set of session lines."""

        for line in lines:
            quantity = quantities[line.id]
            if quantity < 0:
                raise UnprocessingError("Quantity cannot be negative")
            if line.qty != quantity:
                await self._repository.update_line_quantity(
                    line=line, quantity=quantity, mode=mode
                )


    async def _required_tool(self, *, user_id: UUID, lot_id: UUID, role: str):
        """Load an owned tool lot and reject missing or incompatible tools."""

        lot = await self._lot_service.get_unstackable_lot(
            user_id=user_id, lot_id=lot_id
        )
        if lot.origin is None or lot.origin.item is None:
            raise AppError(404, "Tool lot not found")
        item = lot.origin.item
        if role == "finder" and item.finder is None:
            raise UnprocessingError("A finder lot is required")
        if role == "excavator" and item.excavator is None:
            raise UnprocessingError("An excavator lot is required")
        if role == "finder amplifier" and item.finder_amplifier is None:
            raise UnprocessingError("A finder amplifier lot is required")
        return lot

    @staticmethod
    def _validate_identical_finders(finder_lots: list) -> None:
        """Ensure all selected finders share item and tier values."""

        first = finder_lots[0]
        first_item = first.origin.item.id
        first_tier = first.tool_lot.tier
        if any(
            lot.origin.item.id != first_item or lot.tool_lot.tier != first_tier
            for lot in finder_lots[1:]
        ):
            raise UnprocessingError("All finders must have the same item and tier")

    @classmethod
    def _validate_limited_tool_capacity(
        cls, lots: list, *, role: str, clic: int, multiplier: Decimal
    ) -> None:
        """Ensure each limited tool covers the requested decay before repair."""

        for lot in lots:
            if not is_limited_item(lot.origin.item):
                continue
            tt = lot.tool_lot.tt
            if tt is None:
                raise UnprocessingError(f"A limited {role} has no TT value")
            try:
                decay = cls._item_decay(lot.origin.item)
            except UnprocessingError:
                raise UnprocessingError(f"A limited {role} has no decay value")
            if tt < Decimal(clic) * decay * multiplier:
                raise UnprocessingError(
                    f"A limited {role} cannot cover the requested session"
                )

    @classmethod
    def _validate_amplifier_capacity(
        cls, lots: list, *, clic: int, multiplier: Decimal
    ) -> None:
        """Ensure amplifier capacities cover the session without pooling residue."""

        remaining_clicks = clic
        for lot in lots:
            item = lot.origin.item
            if not is_limited_item(item):
                continue
            tt = lot.tool_lot.tt
            if tt is None:
                raise UnprocessingError("A selected limited finder amplifier has no TT value")
            try:
                decay = cls._item_decay(item)
            except UnprocessingError:
                raise UnprocessingError(
                    "A selected finder amplifier has no decay value"
                )
            clicks_supported = int(tt / (decay * multiplier))
            remaining_clicks -= clicks_supported
            if remaining_clicks <= 0:
                return
        raise UnprocessingError(
            "The selected finder amplifiers cannot cover the requested session"
        )

    @classmethod
    def _tool_line(
        cls, lot, clic: int, multiplier: Decimal, *, is_finder: bool = False
    ) -> dict[str, object]:
        """Build a consumed line using the tool cost and search multiplier."""

        item = lot.origin.item
        decay = cls._finder_probe_cost(item) if is_finder else cls._item_decay(item)
        return {
            "lot_id": lot.id,
            "decay": Decimal(clic) * decay * multiplier,
        }

    @staticmethod
    def _item_decay(item: Item) -> Decimal:
        """Return an item's decay or reject incomplete catalogue data."""

        if item.economy is None or item.economy.decay is None:
            raise UnprocessingError("The selected tool has no decay value")
        return item.economy.decay

    @staticmethod
    def _finder_probe_cost(item: Item) -> Decimal:
        """Return the fixed PED cost of one finder probe burn."""

        if item.finder is None or item.finder.ammo_burn is None:
            raise UnprocessingError("The selected finder has no ammo burn value")
        return Decimal(item.finder.ammo_burn) * Decimal("0.05")

    @classmethod
    def _calculate_costs(
        cls,
        *,
        finder_lots: list,
        amplifier_lots: list,
        clic: int,
        multiplier: Decimal,
    ) -> tuple[Decimal, Decimal]:
        """Calculate TT and markup-adjusted TTC for probes and tool decay."""

        finder_item = finder_lots[0].origin.item
        probe_tt = Decimal(clic) * cls._finder_probe_cost(finder_item) * multiplier
        finder_decay_tt = Decimal(clic) * cls._item_decay(finder_item) * multiplier
        total_tt = probe_tt + finder_decay_tt
        total_ttc = probe_tt + cls._with_markup(finder_decay_tt, finder_item)

        remaining_clicks = clic
        for lot in amplifier_lots:
            if remaining_clicks <= 0:
                break
            if not is_limited_item(lot.origin.item):
                continue
            tt = lot.tool_lot.tt
            if tt is None:
                continue
            decay = cls._item_decay(lot.origin.item)
            supported_clicks = min(remaining_clicks, int(tt / (decay * multiplier)))
            amp_decay_tt = Decimal(supported_clicks) * decay * multiplier
            total_tt += amp_decay_tt
            total_ttc += cls._with_markup(amp_decay_tt, lot.origin.item)
            remaining_clicks -= supported_clicks
        return total_tt, total_ttc

    @staticmethod
    def _with_markup(value: Decimal, item: Item) -> Decimal:
        """Apply an item's catalogue markup to a TT cost."""

        economy = item.economy
        if economy is None:
            return value
        if economy.avg_mu_percent is not None:
            return value * economy.avg_mu_percent / Decimal(100)
        if economy.avg_mu_plus is not None:
            return value + economy.avg_mu_plus
        return value


def get_session_mining_service(session: AsyncSession) -> SessionMiningService:
    """Build the mining-session service for a database session."""

    lot_service = get_lot_service(session)
    return SessionMiningService(
        session,
        SessionMiningRepository(session),
        lot_service,
        get_enhancer_service(session, lot_service),
    )
