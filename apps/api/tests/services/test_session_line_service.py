from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

from api.services.session_line_service import SessionLineService


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
