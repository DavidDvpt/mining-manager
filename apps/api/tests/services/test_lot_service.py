from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from api.core.exceptions import AppError, UnprocessingError
from api.db.models import LotKind, SessionLineType
from api.services import lot_service


class TransactionContext:
    """Minimal async transaction context used by service unit tests."""

    async def __aenter__(self):
        """Enter the fake transaction without changing test state."""

        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        """Leave the fake transaction successfully."""

        return False


@pytest.fixture
def session():
    """Return a session double supporting ``async with session.begin()``."""

    value = MagicMock()
    value.begin.return_value = TransactionContext()
    return value


def _session_line(*, line_type=SessionLineType.PRODUCED):
    """Build a session-line double for a lot service scenario."""

    return SimpleNamespace(id=uuid4(), type=line_type, lot_id=None)


async def test_create_lot_delegates_owned_produced_material_creation(
    session, monkeypatch
):
    """Create a material lot from a produced line and ignore ``tt``."""

    repository = AsyncMock()
    line = _session_line()
    expected_lot = SimpleNamespace(id=uuid4())
    repository.get_session_line_for_user.return_value = line
    repository.create.return_value = expected_lot
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_session_line_service", lambda _session: repository)

    result = await lot_service.LotService(
        session, repository, repository, repository
    ).create_lot(
        user_id=uuid4(),
        kind=LotKind.MATERIAL,
        session_line_id=line.id,
        quantity=12,
        tt=Decimal(999),
    )

    assert result is expected_lot
    repository.get_session_line_for_user.assert_awaited_once()
    repository.create.assert_awaited_once_with(
        user_id=repository.create.call_args.kwargs["user_id"],
        session_line=line,
        kind="MATERIAL",
        quantity=12,
        tt=None,
    )


@pytest.mark.parametrize(
    ("kind", "quantity", "tt", "message"),
    [
        (LotKind.TOOL, 2, Decimal(10), "Tool quantity must be 1"),
        (LotKind.TOOL, 1, None, "tt is required for tools"),
    ],
)
async def test_create_lot_rejects_invalid_tool_payload(
    session, monkeypatch, kind, quantity, tt, message
):
    """Reject invalid tool quantity and TT combinations with HTTP 409."""

    repository = AsyncMock()
    line = _session_line()
    repository.get_session_line_for_user.return_value = line
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_session_line_service", lambda _session: repository)

    with pytest.raises(UnprocessingError, match=message) as error:
        await lot_service.LotService(
            session, repository, repository, repository
        ).create_lot(
            user_id=uuid4(),
            kind=kind,
            session_line_id=line.id,
            quantity=quantity,
            tt=tt,
        )

    assert error.value.status_code == 409
    repository.create.assert_not_awaited()


async def test_create_lot_delegates_tool_tt(session, monkeypatch):
    """Persist a tool lot with quantity one and its mutable TT value."""

    repository = AsyncMock()
    line = _session_line()
    expected_lot = SimpleNamespace(id=uuid4())
    repository.get_session_line_for_user.return_value = line
    repository.create.return_value = expected_lot
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_session_line_service", lambda _session: repository)
    tt = Decimal("12.34500")

    result = await lot_service.LotService(
        session, repository, repository, repository
    ).create_lot(
        user_id=uuid4(),
        kind=LotKind.TOOL,
        session_line_id=line.id,
        quantity=1,
        tt=tt,
    )

    assert result is expected_lot
    assert repository.create.call_args.kwargs["kind"] == "TOOL"
    assert repository.create.call_args.kwargs["quantity"] == 1
    assert repository.create.call_args.kwargs["tt"] == tt


async def test_create_lot_rejects_unknown_session_line(session, monkeypatch):
    """Return not found and avoid persistence when the line is unavailable."""

    repository = AsyncMock()
    repository.get_session_line_for_user.return_value = None
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_session_line_service", lambda _session: repository)

    with pytest.raises(AppError) as error:
        await lot_service.LotService(
            session, repository, repository, repository
        ).create_lot(
            user_id=uuid4(),
            kind=LotKind.MATERIAL,
            session_line_id=uuid4(),
            quantity=1,
            tt=None,
        )

    assert error.value.status_code == 404
    repository.create.assert_not_awaited()


async def test_create_lot_rejects_consumed_session_lines(session, monkeypatch):
    """Reject a consumed line because only produced lines create lots."""

    repository = AsyncMock()
    line = _session_line(line_type=SessionLineType.CONSUMED)
    repository.get_session_line_for_user.return_value = line
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_session_line_service", lambda _session: repository)

    with pytest.raises(UnprocessingError, match="Only produced"):
        await lot_service.LotService(
            session, repository, repository, repository
        ).create_lot(
            user_id=uuid4(),
            kind=LotKind.ENHANCER,
            session_line_id=line.id,
            quantity=3,
            tt=None,
        )

    repository.create.assert_not_awaited()


async def test_get_fifo_lots_returns_oldest_first_and_scopes_to_user(
    session, monkeypatch
):
    """Delegate FIFO loading with the authenticated user and item ids."""

    repository = AsyncMock()
    item_id = uuid4()
    expected_lots = [SimpleNamespace(id=uuid4()), SimpleNamespace(id=uuid4())]
    expected_item = SimpleNamespace(id=item_id)
    repository.is_item_stackable.return_value = True
    repository.get_fifo_lots_for_item.return_value = (
        expected_item,
        expected_lots,
        15,
    )
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_item_service", lambda _session: repository)
    user_id = uuid4()

    result = await lot_service.LotService(
        session, repository, repository, repository
    ).get_fifo_lots(
        user_id=user_id, item_id=item_id
    )

    assert result == (expected_item, expected_lots, 15)
    repository.is_item_stackable.assert_awaited_once_with(item_id=item_id)
    repository.get_fifo_lots_for_item.assert_awaited_once_with(
        user_id=user_id, item_id=item_id
    )


async def test_get_fifo_lots_rejects_non_stackable_items(session, monkeypatch):
    """Reject a known non-stackable item with HTTP 409."""

    repository = AsyncMock()
    repository.is_item_stackable.return_value = False
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_item_service", lambda _session: repository)

    with pytest.raises(UnprocessingError, match="not stackable") as error:
        await lot_service.LotService(
            session, repository, repository, repository
        ).get_fifo_lots(
            user_id=uuid4(), item_id=uuid4()
        )

    assert error.value.status_code == 409
    repository.get_fifo_lots_for_item.assert_not_awaited()


async def test_get_fifo_lots_rejects_unknown_items(session, monkeypatch):
    """Reject an unknown item because the response always contains an item."""

    repository = AsyncMock()
    repository.is_item_stackable.return_value = None
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_item_service", lambda _session: repository)

    with pytest.raises(AppError) as error:
        await lot_service.LotService(
            session, repository, repository, repository
        ).get_fifo_lots(user_id=uuid4(), item_id=uuid4())

    assert error.value.status_code == 404
    repository.get_fifo_lots_for_item.assert_not_awaited()


def _lot_with_origin_item(*, quantity=10, reserved=0, stackable_item_id=None):
    """Build a lot double with the source item required for deduction."""

    item = SimpleNamespace(id=stackable_item_id or uuid4())
    origin = SimpleNamespace(item=item)
    return SimpleNamespace(
        id=uuid4(),
        qty=quantity,
        reserved=reserved,
        is_active=True,
        origin=origin,
    )


async def test_get_unstackable_lot_returns_owned_tool_lot(session):
    """Return an owned unstackable lot linked to a tool lot."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item()
    lot.tool_lot = SimpleNamespace(tier=7, tt=12)
    repository.get_unstackable_lot.return_value = lot
    item_service.is_item_stackable.return_value = False

    result = await lot_service.LotService(
        session, repository, item_service, AsyncMock()
    ).get_unstackable_lot(user_id=uuid4(), lot_id=lot.id)

    assert result is lot
    item_service.is_item_stackable.assert_awaited_once_with(
        item_id=lot.origin.item.id
    )


async def test_get_unstackable_lot_rejects_stackable_items(session):
    """Reject an unstackable-lot request for a stackable item with HTTP 409."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item()
    repository.get_unstackable_lot.return_value = lot
    item_service.is_item_stackable.return_value = True

    with pytest.raises(UnprocessingError, match="unstackable") as error:
        await lot_service.LotService(
            session, repository, item_service, AsyncMock()
        ).get_unstackable_lot(user_id=uuid4(), lot_id=lot.id)

    assert error.value.status_code == 409


async def test_get_unstackable_lot_rejects_lots_without_tool_lot(session):
    """Reject unstackable lots that are not linked to a tool lot."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item()
    lot.tool_lot = None
    repository.get_unstackable_lot.return_value = lot
    item_service.is_item_stackable.return_value = False

    with pytest.raises(UnprocessingError, match="unstackable tool lot") as error:
        await lot_service.LotService(
            session, repository, item_service, AsyncMock()
        ).get_unstackable_lot(user_id=uuid4(), lot_id=lot.id)

    assert error.value.status_code == 409


async def test_reserve_quantity_increases_reserved_without_decreasing_stock(session):
    """Reserve available stock while keeping the total quantity unchanged."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item(quantity=10, reserved=2)
    repository.get_origin_with_item.return_value = lot
    item_service.is_item_stackable.return_value = True
    repository.update_quantities.return_value = lot

    result = await lot_service.LotService(
        session, repository, item_service, AsyncMock()
    ).reserve_quantity(
        user_id=uuid4(), lot_id=lot.id, quantity=5
    )

    assert result is lot
    item_service.is_item_stackable.assert_awaited_once_with(
        item_id=lot.origin.item.id
    )
    repository.update_quantities.assert_awaited_once_with(
        lot=lot, quantity=10, reserved=7, is_active=True
    )


async def test_consume_reserved_quantity_decreases_stock_and_reservation(session):
    """Consume a reservation from both total and reserved quantities."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item(quantity=10, reserved=2)
    repository.get_origin_with_item.return_value = lot
    item_service.is_item_stackable.return_value = True
    repository.update_quantities.return_value = lot

    await lot_service.LotService(
        session, repository, item_service, AsyncMock()
    ).consume_reserved_quantity(
        user_id=uuid4(), lot_id=lot.id, quantity=2
    )

    repository.update_quantities.assert_awaited_once_with(
        lot=lot, quantity=8, reserved=0, is_active=True
    )


async def test_reserve_quantity_rejects_quantity_over_available_stock(
    session,
):
    """Reject a reservation that would exceed available stock with HTTP 409."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item(quantity=10, reserved=4)
    repository.get_origin_with_item.return_value = lot
    item_service.is_item_stackable.return_value = True

    with pytest.raises(UnprocessingError, match="available") as error:
        await lot_service.LotService(
            session, repository, item_service, AsyncMock()
        ).reserve_quantity(
            user_id=uuid4(), lot_id=lot.id, quantity=7
        )

    assert error.value.status_code == 409
    repository.update_quantities.assert_not_awaited()


async def test_consume_reserved_quantity_rejects_unreserved_quantity(
    session,
):
    """Reject consumption when the lot has insufficient reservation."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item(reserved=2)
    repository.get_origin_with_item.return_value = lot
    item_service.is_item_stackable.return_value = True

    with pytest.raises(UnprocessingError, match="reserved") as error:
        await lot_service.LotService(
            session, repository, item_service, AsyncMock()
        ).consume_reserved_quantity(
            user_id=uuid4(), lot_id=lot.id, quantity=3
        )

    assert error.value.status_code == 409
    repository.update_quantities.assert_not_awaited()


async def test_reserve_quantity_returns_lot_without_updating_for_zero_quantity(
    session,
):
    """Treat zero reservation as a no-op and avoid the quantity update."""

    repository = AsyncMock()
    lot = _lot_with_origin_item()
    repository.get_origin_with_item.return_value = lot

    result = await lot_service.LotService(
        session, repository, AsyncMock(), AsyncMock()
    ).reserve_quantity(
        user_id=uuid4(), lot_id=lot.id, quantity=0
    )

    assert result is lot
    repository.update_quantities.assert_not_awaited()


async def test_consume_reserved_quantity_deactivates_empty_lot(session):
    """Deactivate a lot after consuming its final unreserved quantity."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item(quantity=10, reserved=10)
    repository.get_origin_with_item.return_value = lot
    item_service.is_item_stackable.return_value = True
    repository.update_quantities.return_value = lot

    await lot_service.LotService(
        session, repository, item_service, AsyncMock()
    ).consume_reserved_quantity(
        user_id=uuid4(), lot_id=lot.id, quantity=10
    )

    repository.update_quantities.assert_awaited_once_with(
        lot=lot, quantity=0, reserved=0, is_active=False
    )


async def test_reserve_quantity_rejects_non_stackable_item(session):
    """Reject reservation for a known non-stackable item with HTTP 409."""

    repository = AsyncMock()
    item_service = AsyncMock()
    lot = _lot_with_origin_item()
    repository.get_origin_with_item.return_value = lot
    item_service.is_item_stackable.return_value = False

    with pytest.raises(UnprocessingError, match="not stackable") as error:
        await lot_service.LotService(
            session, repository, item_service, AsyncMock()
        ).reserve_quantity(
            user_id=uuid4(), lot_id=lot.id, quantity=1
        )

    assert error.value.status_code == 409
    repository.update_quantities.assert_not_awaited()
