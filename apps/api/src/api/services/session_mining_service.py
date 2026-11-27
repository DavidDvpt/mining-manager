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

from .excavator_service import ExcavatorService, get_excavator_service
from .finder_amplifier_service import (
    FinderAmplifierService,
    get_finder_amplifier_service,
)
from .finder_service import FinderService, get_finder_service
from .item_service import is_limited_item
from .session_line_service import SessionLineService, get_session_line_service
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
        session_line_service: SessionLineService,
        finder_service: FinderService,
        excavator_service: ExcavatorService,
        finder_amplifier_service: FinderAmplifierService,
    ) -> None:
        """Bind mining persistence and domain services for owned equipment and session lines."""

        self._session = session
        self._repository = repository
        self._lot_service = lot_service
        self._session_line_service = session_line_service
        self._finder_service = finder_service
        self._excavator_service = excavator_service
        self._finder_amplifier_service = finder_amplifier_service

    async def get_open_session(self, *, user_id: UUID) -> Session | None:
        """Return the user's open mining session for navigation availability."""

        return await self._repository.get_open_session(user_id=user_id)

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
        """Create one owned setup after validating model, pooled L capacity and enhancer tiers.

        Plan finder decay in selection order and estimate ammo and other tool costs.
        Excavator and enhancer use is confirmed at closing.
        """

        if clic < 1:
            raise UnprocessingError("clic must be greater than zero")
        if not finders or not excavators:
            raise UnprocessingError("Select at least one finder and excavator")
        all_tools = finders + excavators + finder_amplifiers
        if len(set(all_tools)) != len(all_tools):
            raise UnprocessingError("An equipment lot cannot be selected twice")
        multiplier = Decimal(len(search_type.value))

        async with _transaction_scope(self._session):
            await self._repository.lock_user(user_id=user_id)
            if await self._repository.get_open_session(user_id=user_id) is not None:
                raise UnprocessingError("A mining session is already open")
            if zone_id is not None and await self._repository.get_zone(
                zone_id=zone_id, user_id=user_id
            ) is None:
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

            tool_lines = self._build_tool_lines(
                finder_lots=finder_lots, excavator_lots=excavator_lots,
                amplifier_lots=amplifier_lots, clic=clic, multiplier=multiplier,
            )
            session = await self._repository.create(
                user_id=user_id, clic=clic, zone_id=zone_id,
                search_type=search_type, tool_lines=tool_lines,
                enhancer_lines=[],
            )
            enhancer_data = []
            for selected, tools, role in (
                (finder_enhancers, finder_lots, "FINDER"),
                (excavator_enhancers, excavator_lots, "EXCAVATOR"),
            ):
                tier = min(lot.tool_lot.tier or 0 for lot in tools)
                enhancer_data.extend(await self._session_line_service.prepare_mining_enhancers(
                    session_id=session.id, user_id=user_id, item_ids=selected,
                    tool=role, minimum_tier=tier,
                ))

            total_tt, total_ttc = self._calculate_costs(
                finder_lots=finder_lots,
                amplifier_lots=amplifier_lots,
                clic=clic,
                multiplier=multiplier,
                search_type=search_type,
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

        Each finder line must match its planned decay, which is consumed from L lots.
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
            finder_lines = [line for line in tool_lines if self._line_item(line).finder is not None]
            if finder_lines:
                if any(line.decay is None for line in finder_lines):
                    raise UnprocessingError("Finder lines are missing their planned decay")
                if any(tool_decays[line.id] != line.decay.decay_ttc for line in finder_lines):
                    raise UnprocessingError("Finder decay must match the planned allocation")
                # Keep stock updates in a stable order independent of the allocation.
                for line in sorted(finder_lines, key=lambda line: (line.lot.tool_lot.tt or Decimal(0), str(line.lot_id))):
                    await self._lot_service.consume_tool_decay(
                        user_id=user_id, lot_id=line.lot_id, decay=line.decay.decay_ttc
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
                remaining_tt = amplifier_tts[line.id]
                lot.tool_lot.tt = remaining_tt
                item = lot.origin.item if lot.origin is not None else None
                if item is not None and is_limited_item(item) and remaining_tt <= 0:
                    lot.qty = 0
                    lot.reserved = 0
                    lot.is_active = False

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
                if line.quantity != quantity:
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
            if line.quantity != quantity:
                await self._repository.update_line_quantity(
                    line=line, quantity=quantity, mode=mode
                )


    async def _required_tool(self, *, user_id: UUID, lot_id: UUID, role: str):
        """Load an owned role-compatible tool and reject inactive, empty or reserved stock."""

        if role == "finder":
            lot = await self._finder_service.get_owned_lot(user_id=user_id, lot_id=lot_id)
        elif role == "excavator":
            lot = await self._excavator_service.get_owned_lot(user_id=user_id, lot_id=lot_id)
        elif role == "finder amplifier":
            lot = await self._finder_amplifier_service.get_owned_lot(user_id=user_id, lot_id=lot_id)
        else:
            raise UnprocessingError("Unknown tool role")
        if not lot.is_active or lot.qty - lot.reserved < 1:
            raise UnprocessingError("The selected tool is no longer available")
        return lot

    @staticmethod
    def _validate_identical_finders(finder_lots: list) -> None:
        """Require one finder model while allowing different tiers and distinct owned lots."""

        first_item = finder_lots[0].origin.item.id
        if len({lot.id for lot in finder_lots}) != len(finder_lots):
            raise UnprocessingError("A finder lot cannot be selected twice")
        if any(lot.origin.item.id != first_item for lot in finder_lots):
            raise UnprocessingError("All finders must have the same item")

    @classmethod
    def _validate_limited_tool_capacity(
        cls, lots: list, *, role: str, clic: int, multiplier: Decimal
    ) -> None:
        """Require sufficient pooled L TT, with each additional lot needed when selected."""

        if any(not is_limited_item(lot.origin.item) for lot in lots):
            if len(lots) > 1:
                raise UnprocessingError("Only one unlimited finder is needed")
            return
        if any(lot.tool_lot.tt is None for lot in lots):
            raise UnprocessingError(f"A limited {role} has no TT value")
        total_tt = sum((lot.tool_lot.tt for lot in lots), Decimal(0))
        required = Decimal(clic) * cls._item_decay(lots[0].origin.item) * multiplier
        if total_tt < required:
            raise UnprocessingError(f"Limited {role} TT must cover the requested decay")
        if len(lots) > 1 and total_tt - lots[-1].tool_lot.tt >= required:
            raise UnprocessingError("Remove finders that are not needed for the session")

    @classmethod
    def _validate_amplifier_capacity(
        cls, lots: list, *, clic: int, multiplier: Decimal
    ) -> None:
        """Require one amplifier model and pool whole clicks per L lot, ignoring residue."""

        if len({lot.id for lot in lots}) != len(lots):
            raise UnprocessingError("An amplifier lot cannot be selected twice")
        if len({lot.origin.item.id for lot in lots}) != 1:
            raise UnprocessingError("All finder amplifiers must have the same item")
        if any(not is_limited_item(lot.origin.item) for lot in lots):
            return
        capacity = 0
        for lot in lots:
            tt = lot.tool_lot.tt
            if tt is None:
                raise UnprocessingError("A selected limited finder amplifier has no TT value")
            decay = cls._item_decay(lot.origin.item)
            if decay <= 0:
                raise UnprocessingError("A selected finder amplifier has no decay value")
            capacity += int(tt / (decay * multiplier))
        if capacity < clic:
            raise UnprocessingError("The selected finder amplifiers cannot cover the requested session")

    @classmethod
    def _build_tool_lines(
        cls, *, finder_lots: list, excavator_lots: list, amplifier_lots: list,
        clic: int, multiplier: Decimal,
    ) -> list[dict[str, object]]:
        """Allocate finder decay in selection order and amp clicks once; defer excavator use."""

        required_decay = Decimal(clic) * cls._item_decay(finder_lots[0].origin.item) * multiplier
        lines = cls._allocate_finder_decay(finder_lots, required_decay)
        lines.extend({"lot_id": lot.id} for lot in excavator_lots)
        remaining_clicks = clic
        for lot in amplifier_lots:
            decay = cls._item_decay(lot.origin.item) * multiplier
            if decay <= 0:
                raise UnprocessingError("A selected finder amplifier has no decay value")
            capacity = int((lot.tool_lot.tt or 0) / decay) if is_limited_item(lot.origin.item) else remaining_clicks
            used = min(remaining_clicks, capacity)
            lines.append({"lot_id": lot.id, "decay": Decimal(used) * decay})
            remaining_clicks -= used
        return lines

    @staticmethod
    def _allocate_finder_decay(lots: list, total_decay: Decimal) -> list[dict[str, object]]:
        """Distribute a single decay budget across finders in the supplied selection order."""

        remaining = total_decay
        lines = []
        for lot in lots:
            available = lot.tool_lot.tt if is_limited_item(lot.origin.item) else remaining
            used = min(remaining, available or Decimal(0))
            lines.append({"lot_id": lot.id, "decay": used})
            remaining -= used
        if remaining > 0:
            raise UnprocessingError("The selected finders cannot cover the session decay")
        return lines

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
        search_type: SessionMiningSearchType,
    ) -> tuple[Decimal, Decimal]:
        """Estimate ammo (E=1/O=2/EO=3), finder decay once, and sequential amplifier use."""

        finder_item = finder_lots[0].origin.item
        ammo_multiplier = sum({"E": 1, "O": 2, "T": 1}[kind] for kind in search_type.value)
        probe_tt = Decimal(clic) * cls._finder_probe_cost(finder_item) * ammo_multiplier
        finder_decay_tt = Decimal(clic) * cls._item_decay(finder_item) * multiplier
        total_tt = probe_tt + finder_decay_tt
        total_ttc = probe_tt + cls._with_markup(finder_decay_tt, finder_item)

        remaining_clicks = clic
        for lot in amplifier_lots:
            if remaining_clicks <= 0:
                break
            decay = cls._item_decay(lot.origin.item)
            capacity = int((lot.tool_lot.tt or 0) / (decay * multiplier)) if is_limited_item(lot.origin.item) else remaining_clicks
            supported_clicks = min(remaining_clicks, capacity)
            amp_decay_tt = Decimal(supported_clicks) * decay * multiplier
            total_tt += amp_decay_tt
            total_ttc += cls._with_markup(amp_decay_tt, lot.origin.item)
            remaining_clicks -= supported_clicks
        return total_tt, total_ttc

    @staticmethod
    def _with_markup(value: Decimal, item: Item) -> Decimal:
        """Apply catalogue markup only to consumed L value; UL value stays at 100 percent."""

        if value == 0 or not is_limited_item(item):
            return value
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
        get_session_line_service(session),
        get_finder_service(session, lot_service),
        get_excavator_service(session, lot_service),
        get_finder_amplifier_service(session, lot_service),
    )
