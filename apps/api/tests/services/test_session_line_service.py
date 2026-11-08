from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from api.core.exceptions import UnprocessingError
from api.db.models import SessionLineType
from api.services.session_line_service import SessionLineService


class TransactionContext:
    """Minimal async transaction context used by service unit tests."""

    async def __aenter__(self):
        """Enter the fake transaction."""

        return self

    async def __aexit__(self, _exc_type, _exc_value, _traceback):
        """Leave the fake transaction without suppressing exceptions."""

        return False


def _service():
    """Build a session-line service with isolated dependency doubles."""

    session = MagicMock()
    session.in_transaction.return_value = False
    session.begin.return_value = TransactionContext()
    repository = AsyncMock()
    repository.session = session
    session_service = AsyncMock()
    session_service.get_mining_session_for_user.return_value = SimpleNamespace(
        ended_at=None
    )
    mining_loot_service = AsyncMock()
    mining_loot_service.get_item.return_value = SimpleNamespace(id=uuid4())
    return (
        SessionLineService(repository, session_service, mining_loot_service),
        repository,
        session_service,
        mining_loot_service,
    )


async def test_get_session_line_for_user_delegates_with_scope():
    """Return the owned session line supplied by the repository."""

    repository = AsyncMock()
    expected_line = SimpleNamespace(id=uuid4())
    repository.get_session_line_for_user.return_value = expected_line
    service = SessionLineService(repository)
    session_line_id = uuid4()
    user_id = uuid4()

    result = await service.get_session_line_for_user(
        session_line_id=session_line_id,
        user_id=user_id,
    )

    assert result is expected_line
    repository.get_session_line_for_user.assert_awaited_once_with(
        session_line_id=session_line_id,
        user_id=user_id,
    )


async def test_get_session_line_for_user_preserves_missing_result():
    """Return ``None`` when the repository cannot find an owned line."""

    repository = AsyncMock()
    repository.get_session_line_for_user.return_value = None

    result = await SessionLineService(repository).get_session_line_for_user(
        session_line_id=uuid4(),
        user_id=uuid4(),
    )

    assert result is None


async def test_create_produced_line_validates_mining_loot_and_delegates():
    """Create a produced line only after the mining-loot service finds its item."""

    service, repository, session_service, mining_loot_service = _service()
    session_id = uuid4()
    item_id = uuid4()
    expected_line = SimpleNamespace(id=uuid4())
    item = SimpleNamespace(id=item_id)
    mining_loot_service.get_item.return_value = item
    repository.create_produced_line.return_value = expected_line

    result = await service.create_produced_line(
        session_id=session_id,
        item_id=item_id,
        quantity=4,
        user_id=uuid4(),
    )

    assert result is expected_line
    session_service.get_mining_session_for_user.assert_awaited_once()
    mining_loot_service.get_item.assert_awaited_once_with(item_id=item_id)
    repository.create_produced_line.assert_awaited_once_with(
        session=session_service.get_mining_session_for_user.return_value,
        item=item,
        quantity=4,
    )


async def test_update_produced_line_changes_only_quantity():
    """Delegate a produced-line quantity update within the session scope."""

    service, repository, _session_service, _mining_loot_service = _service()
    line = SimpleNamespace(id=uuid4(), type=SessionLineType.PRODUCED)
    repository.get_session_line_for_user.return_value = line
    repository.update_quantity.return_value = line
    session_id = uuid4()
    line_id = line.id
    user_id = uuid4()

    result = await service.update_produced_line_quantity(
        session_id=session_id,
        session_line_id=line_id,
        quantity=9,
        user_id=user_id,
    )

    assert result is line
    repository.get_session_line_for_user.assert_awaited_once_with(
        session_id=session_id,
        session_line_id=line_id,
        user_id=user_id,
    )
    repository.update_quantity.assert_awaited_once_with(line=line, quantity=9)


async def test_delete_produced_line_deletes_lines_without_origin_lot():
    """Delete a produced line when no inventory lot references it."""

    service, repository, _session_service, _mining_loot_service = _service()
    line = SimpleNamespace(id=uuid4(), type=SessionLineType.PRODUCED)
    repository.get_session_line_for_user.return_value = line
    repository.has_origin_lot.return_value = False

    await service.delete_produced_line(
        session_id=uuid4(),
        session_line_id=line.id,
        user_id=uuid4(),
    )

    repository.delete_line.assert_awaited_once_with(line=line)


async def test_delete_produced_line_rejects_lines_with_origin_lot():
    """Reject deletion when an inventory lot uses the line as its origin."""

    service, repository, _session_service, _mining_loot_service = _service()
    line = SimpleNamespace(id=uuid4(), type=SessionLineType.PRODUCED)
    repository.get_session_line_for_user.return_value = line
    repository.has_origin_lot.return_value = True

    with pytest.raises(UnprocessingError, match="originating lot"):
        await service.delete_produced_line(
            session_id=uuid4(),
            session_line_id=line.id,
            user_id=uuid4(),
        )

    repository.delete_line.assert_not_awaited()


async def test_increment_produced_line_creates_missing_item_line():
    """Create a produced line when no line exists for the requested item."""

    service, repository, session_service, mining_loot_service = _service()
    session_id = uuid4()
    item_id = uuid4()
    item = SimpleNamespace(id=item_id)
    expected_line = SimpleNamespace(id=uuid4(), quantity=4)
    repository.get_produced_line_for_item.return_value = None
    mining_loot_service.get_item.return_value = item
    repository.create_produced_line.return_value = expected_line

    result = await service.increment_produced_line_for_item(
        session_id=session_id,
        item_id=item_id,
        quantity=4,
        user_id=uuid4(),
    )

    assert result is expected_line
    repository.create_produced_line.assert_awaited_once_with(
        session=session_service.get_mining_session_for_user.return_value,
        item=item,
        quantity=4,
    )
    repository.update_quantity.assert_not_awaited()


async def test_increment_produced_line_updates_existing_item_line():
    """Add the requested quantity to an existing produced item line."""

    service, repository, _session_service, _mining_loot_service = _service()
    line = SimpleNamespace(id=uuid4(), quantity=3)
    repository.get_produced_line_for_item.return_value = line
    repository.has_origin_lot.return_value = False
    repository.update_quantity.return_value = line

    result = await service.increment_produced_line_for_item(
        session_id=uuid4(),
        item_id=uuid4(),
        quantity=2,
        user_id=uuid4(),
    )

    assert result is line
    repository.update_quantity.assert_awaited_once_with(line=line, quantity=5)
    repository.create_produced_line.assert_not_awaited()


async def test_increment_produced_line_rejects_lines_with_origin_lot():
    """Reject claim increments when the produced line already created a lot."""

    service, repository, _session_service, _mining_loot_service = _service()
    line = SimpleNamespace(id=uuid4(), quantity=3)
    repository.get_produced_line_for_item.return_value = line
    repository.has_origin_lot.return_value = True

    with pytest.raises(UnprocessingError, match="cannot be incremented"):
        await service.increment_produced_line_for_item(
            session_id=uuid4(),
            item_id=uuid4(),
            quantity=2,
            user_id=uuid4(),
        )

    repository.update_quantity.assert_not_awaited()
