from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from api.api.deps import get_current_user
from api.api.v1 import mining_session_controller
from api.core.config import get_settings
from api.db import get_session
from api.main import app


def endpoint(path: str) -> str:
    """Build an API v1 endpoint path for a controller test."""

    return f"{get_settings().api_v1_prefix}{path}"


def test_close_mining_session_maps_payload_to_service(monkeypatch):
    """Forward every close payload collection to the mining-session service."""

    user_id = uuid4()
    session_id = uuid4()
    finder_line_id = uuid4()
    excavator_line_id = uuid4()
    amplifier_line_id = uuid4()
    enhancer_line_id = uuid4()
    produced_line_id = uuid4()
    calls = {}

    async def fake_close(**kwargs):
        """Capture close arguments and return a serialized session fixture."""

        calls.update(kwargs)
        return SimpleNamespace(
            id=session_id,
            user_id=user_id,
            started_at=date(2026, 11, 1),
            ended_at=date(2026, 11, 4),
        )

    monkeypatch.setattr(
        mining_session_controller,
        "get_session_mining_service",
        lambda _session: SimpleNamespace(close=fake_close),
    )

    async def fake_session():
        """Yield a placeholder database dependency for the controller test."""

        yield object()

    async def fake_current_user():
        """Return the authenticated user used by the request."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    app.dependency_overrides[get_session] = fake_session
    app.dependency_overrides[get_current_user] = fake_current_user
    payload = {
        "finders": [{"lineId": str(finder_line_id), "decay": "1.10"}],
        "excavators": [{"lineId": str(excavator_line_id), "decay": "2.20"}],
        "amplifiers": [
            {
                "lineId": str(amplifier_line_id),
                "decay": "0.30",
                "tt": "12.50",
            }
        ],
        "enhancers": [{"lineId": str(enhancer_line_id), "quantity": 4}],
        "produced": [{"lineId": str(produced_line_id), "quantity": 7}],
    }
    try:
        with TestClient(app) as client:
            response = client.patch(
                endpoint(f"/mining/{session_id}/close"), json=payload
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json() == {
        "id": str(session_id),
        "userId": str(user_id),
        "startedAt": "2026-11-01",
        "endedAt": "2026-11-04",
    }
    assert calls == {
        "user_id": user_id,
        "session_id": session_id,
        "tool_decays": {
            finder_line_id: Decimal("1.10"),
            excavator_line_id: Decimal("2.20"),
            amplifier_line_id: Decimal("0.30"),
        },
        "amplifier_tts": {amplifier_line_id: Decimal("12.50")},
        "enhancer_quantities": {enhancer_line_id: 4},
        "produced_quantities": {produced_line_id: 7},
    }


def test_current_mining_session_returns_null_without_an_open_session(monkeypatch):
    """Expose authenticated open-session absence without allowing cross-user lookup."""

    user_id = uuid4()
    calls = {}

    async def fake_get_open_session(**kwargs):
        """Capture the authenticated owner used for the session lookup."""

        calls.update(kwargs)
        return None

    async def fake_session():
        """Provide a placeholder database dependency for this request."""

        yield object()

    async def fake_user():
        """Return the signed-in owner independently of request parameters."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    monkeypatch.setattr(mining_session_controller, "get_session_mining_service", lambda _: SimpleNamespace(get_open_session=fake_get_open_session))
    app.dependency_overrides[get_session] = fake_session
    app.dependency_overrides[get_current_user] = fake_user
    try:
        with TestClient(app) as client:
            response = client.get(endpoint("/mining/current"))
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json() is None
    assert calls == {"user_id": user_id}
