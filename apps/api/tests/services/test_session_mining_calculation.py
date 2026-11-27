"""Regression coverage for mining estimates, pooled L TT and repairable unlimited tools."""

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from api.core.exceptions import UnprocessingError
from api.db.models import SessionMiningSearchType, SessionLineType
from api.services.session_mining_service import SessionMiningService


def equipment_lot(*, role="finder", limited=True, tt="183", decay="2", tier=0, item=None):
    """Build a tool lot with the catalogue fields used by mining calculations."""

    if item is None:
        detail = SimpleNamespace(is_limited=limited, ammo_burn=10)
        item = SimpleNamespace(
            id=uuid4(), name="Tool (L)" if limited else "Tool", finder=None, excavator=None, finder_amplifier=None,
            refiner=None, enhancer=None, economy=SimpleNamespace(
                decay=Decimal(decay), avg_mu_percent=None, avg_mu_plus=None
            ),
        )
        setattr(item, role, detail)
    return SimpleNamespace(
        id=uuid4(), origin=SimpleNamespace(item=item),
        tool_lot=SimpleNamespace(tt=Decimal(tt) if tt is not None else None, tier=tier),
    )


@pytest.mark.parametrize("search_type,ammo", [(SessionMiningSearchType.E, "5"), (SessionMiningSearchType.O, "10"), (SessionMiningSearchType.EO, "15")])
def test_mining_ammo_and_finder_decay(search_type, ammo):
    """Apply E/O/EO ammo multipliers independently from the tool decay multiplier."""

    finder = equipment_lot(decay="0.1")
    count = Decimal(len(search_type.value))
    tt, ttc = SessionMiningService._calculate_costs(
        finder_lots=[finder], amplifier_lots=[], clic=10,
        multiplier=count, search_type=search_type,
    )
    assert tt == Decimal(ammo) + count
    assert ttc == tt


def test_finders_pool_tt_across_different_tiers():
    """Allow one finder model with different tiers and enough combined limited TT."""

    first = equipment_lot(tt="6", decay="1", tier=4)
    second = equipment_lot(tt="6", tier=0, item=first.origin.item)
    SessionMiningService._validate_identical_finders([first, second])
    SessionMiningService._validate_limited_tool_capacity([first, second], role="finder", clic=10, multiplier=Decimal(1))
    with pytest.raises(UnprocessingError):
        SessionMiningService._validate_limited_tool_capacity([first, second], role="finder", clic=13, multiplier=Decimal(1))


@pytest.mark.parametrize("multiplier,capacity", [(1, 182), (2, 90)])
def test_amplifier_residue_is_not_pooled(multiplier, capacity):
    """Two 183-TT amplifiers with decay 2 cover 182 or 90 whole clicks."""

    first = equipment_lot(role="finder_amplifier")
    second = equipment_lot(role="finder_amplifier", item=first.origin.item)
    SessionMiningService._validate_amplifier_capacity([first, second], clic=capacity, multiplier=Decimal(multiplier))
    with pytest.raises(UnprocessingError):
        SessionMiningService._validate_amplifier_capacity([first, second], clic=capacity + 1, multiplier=Decimal(multiplier))


def test_unlimited_tools_can_be_repaired():
    """Do not impose current TT limits on unlimited finders or amplifiers."""

    finder = equipment_lot(limited=False, tt="0")
    amplifier = equipment_lot(role="finder_amplifier", limited=False, tt="0")
    SessionMiningService._validate_limited_tool_capacity([finder], role="finder", clic=100, multiplier=Decimal(2))
    SessionMiningService._validate_amplifier_capacity([amplifier], clic=100, multiplier=Decimal(2))
    tt, _ = SessionMiningService._calculate_costs(finder_lots=[finder], amplifier_lots=[amplifier], clic=100, multiplier=Decimal(2), search_type=SessionMiningSearchType.EO)
    assert tt == Decimal("950")


def test_tool_lines_do_not_multiply_session_decay_by_number_of_tools():
    """Allocate finder decay once and defer excavator costs to confirmation."""

    finder = equipment_lot(tt="6", decay="1")
    second = equipment_lot(tt="6", item=finder.origin.item)
    excavator = equipment_lot(role="excavator")
    lines = SessionMiningService._build_tool_lines(finder_lots=[finder, second], excavator_lots=[excavator], amplifier_lots=[], clic=10, multiplier=Decimal(1))
    assert [line.get("decay") for line in lines] == [Decimal(6), Decimal(4), None]


def test_multiple_amplifier_models_are_rejected():
    """Reject a crafted request mixing amplifier models despite sufficient stock."""

    with pytest.raises(UnprocessingError):
        SessionMiningService._validate_amplifier_capacity([equipment_lot(role="finder_amplifier"), equipment_lot(role="finder_amplifier")], clic=1, multiplier=Decimal(1))



def test_finders_reject_unnecessary_limited_and_unlimited_tools():
    """One sufficient L finder or repairable UL finder must stand alone."""

    first = equipment_lot(tt="10", decay="1")
    second = equipment_lot(tt="2", item=first.origin.item)
    with pytest.raises(UnprocessingError):
        SessionMiningService._validate_limited_tool_capacity([first, second], role="finder", clic=10, multiplier=Decimal(1))
    SessionMiningService._validate_limited_tool_capacity([first], role="finder", clic=10, multiplier=Decimal(1))
    unlimited = equipment_lot(limited=False, tt="0")
    with pytest.raises(UnprocessingError):
        SessionMiningService._validate_limited_tool_capacity([unlimited, equipment_lot(item=unlimited.origin.item)], role="finder", clic=10, multiplier=Decimal(1))


@pytest.mark.parametrize("second_tt", ["3", "10"])
def test_finder_decay_follows_selection_order(second_tt):
    """Keep the first finder before a lower-TT lot or one that could cover the session alone."""

    first = equipment_lot(tt="8", decay="1")
    second = equipment_lot(tt=second_tt, item=first.origin.item)
    SessionMiningService._validate_limited_tool_capacity(
        [first, second], role="finder", clic=10, multiplier=Decimal(1)
    )
    assert SessionMiningService._allocate_finder_decay([first, second], Decimal(10)) == [
        {"lot_id": first.id, "decay": Decimal(8)},
        {"lot_id": second.id, "decay": Decimal(2)},
    ]


async def test_close_consumes_each_finders_allocated_share_once():
    """Use each stored allocation at closing even when it differs from TT order."""

    first = equipment_lot(tt="8", decay="1")
    second = equipment_lot(tt="3", item=first.origin.item)
    lines = [SimpleNamespace(id=uuid4(), lot=lot, lot_id=lot.id, type=SessionLineType.CONSUMED, decay=SimpleNamespace(decay_ttc=Decimal(decay))) for lot, decay in [(first, 8), (second, 2)]]
    session = MagicMock()
    session.in_transaction.return_value = False
    session.begin.return_value = AsyncMock()
    repository = AsyncMock()
    repository.get_session_for_close.return_value = SimpleNamespace(lines=lines, ended_at=None)
    lots = AsyncMock()
    service = SessionMiningService(session, repository, lots, AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock())
    await service.close(user_id=uuid4(), session_id=uuid4(), tool_decays={lines[0].id: Decimal(8), lines[1].id: Decimal(2)}, amplifier_tts={}, enhancer_quantities={}, produced_quantities={})
    assert [call.kwargs["lot_id"] for call in lots.consume_tool_decay.await_args_list] == [second.id, first.id]
    assert [call.kwargs["decay"] for call in lots.consume_tool_decay.await_args_list] == [Decimal(2), Decimal(8)]
    lots.consume_tool_decay.reset_mock()
    with pytest.raises(UnprocessingError):
        await service.close(user_id=uuid4(), session_id=uuid4(), tool_decays={line.id: Decimal(10) for line in lines}, amplifier_tts={}, enhancer_quantities={}, produced_quantities={})
    lots.consume_tool_decay.assert_not_awaited()


@pytest.mark.parametrize("limited,percent,plus,expected", [(False, "150", "10", "2"), (False, None, "10", "2"), (True, "150", None, "3"), (True, None, None, "2")])
def test_estimated_ttc_marks_up_only_limited_items(limited, percent, plus, expected):
    """Use catalogue markup for L costs and keep unlimited costs at exactly TT."""

    lot = equipment_lot(limited=limited)
    item = lot.origin.item
    item.economy.avg_mu_percent = Decimal(percent) if percent is not None else None
    item.economy.avg_mu_plus = Decimal(plus) if plus is not None else None
    assert SessionMiningService._with_markup(Decimal(2), item) == Decimal(expected)
    assert SessionMiningService._with_markup(Decimal(0), item) == Decimal(0)
