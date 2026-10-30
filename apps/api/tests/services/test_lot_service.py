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
    monkeypatch,
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
        object(), repository, repository, repository
    ).get_fifo_lots(
        user_id=user_id, item_id=item_id
    )

    assert result == (expected_item, expected_lots, 15)
    repository.is_item_stackable.assert_awaited_once_with(item_id=item_id)
    repository.get_fifo_lots_for_item.assert_awaited_once_with(
        user_id=user_id, item_id=item_id
    )


async def test_get_fifo_lots_rejects_non_stackable_items(monkeypatch):
    """Reject a known non-stackable item with HTTP 409."""

    repository = AsyncMock()
    repository.is_item_stackable.return_value = False
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_item_service", lambda _session: repository)

    with pytest.raises(UnprocessingError, match="not stackable") as error:
        await lot_service.LotService(
            object(), repository, repository, repository
        ).get_fifo_lots(
            user_id=uuid4(), item_id=uuid4()
        )

    assert error.value.status_code == 409
    repository.get_fifo_lots_for_item.assert_not_awaited()


async def test_get_fifo_lots_rejects_unknown_items(monkeypatch):
    """Reject an unknown item because the response always contains an item."""

    repository = AsyncMock()
    repository.is_item_stackable.return_value = None
    monkeypatch.setattr(lot_service, "LotRepository", lambda _session: repository)
    monkeypatch.setattr(lot_service, "get_item_service", lambda _session: repository)

    with pytest.raises(AppError) as error:
        await lot_service.LotService(
            object(), repository, repository, repository
        ).get_fifo_lots(user_id=uuid4(), item_id=uuid4())

    assert error.value.status_code == 404
    repository.get_fifo_lots_for_item.assert_not_awaited()
