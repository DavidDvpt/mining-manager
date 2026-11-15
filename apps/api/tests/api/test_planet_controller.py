from datetime import date
from types import SimpleNamespace
from uuid import uuid4

from fastapi.testclient import TestClient

from api.api.deps import get_current_user
from api.api.v1 import planet_controller
from api.core.config import get_settings
from api.db import get_session
from api.main import app


def endpoint(path: str) -> str:
    """Build an API v1 endpoint path for a planet controller test."""

    return f"{get_settings().api_v1_prefix}{path}"


def _planet(planet_id):
    """Build a planet response fixture."""

    return SimpleNamespace(
        id=planet_id,
        name="Amethera",
        created_at=date(2026, 1, 1),
        updated_at=None,
    )


def _zone(zone_id, planet_id, user_id):
    """Build a zone response fixture with its owner and planet identifiers."""

    return SimpleNamespace(
        id=zone_id,
        name="Nea's Place",
        planete_id=planet_id,
        user_id=user_id,
        created_at=date(2026, 1, 1),
        updated_at=None,
    )


def _authenticated(user_id):
    """Return the dependency override for an authenticated test user."""

    async def current_user():
        """Return the test user's authentication payload."""

        return {"id": user_id, "role": "USER", "pseudo": "test-user"}

    return current_user


def _override_session():
    """Return a placeholder database dependency for controller tests."""

    async def session():
        """Yield a placeholder request session."""

        yield object()

    return session


def test_planet_read_endpoints_serialize_service_entities(monkeypatch):
    """Serialize planets and user-owned zones for every read endpoint."""

    user_id = uuid4()
    planet_id = uuid4()
    zone_id = uuid4()
    zone = _zone(zone_id, planet_id, user_id)
    calls = []

    class FakeService:
        async def get_all(self):
            """Return the planet fixture."""

            calls.append(("get_all",))
            return [_planet(planet_id)]

        async def get_by_id(self, requested_planet_id):
            """Return the requested planet fixture."""

            calls.append(("get_by_id", requested_planet_id))
            return _planet(requested_planet_id)

        async def get_zones_for_planet(self, *, planet_id, user_id):
            """Return zones for the requested planet and user."""

            calls.append(("get_zones_for_planet", planet_id, user_id))
            return [zone]

        async def get_zone(self, *, planet_id, zone_id, user_id):
            """Return the requested owned zone."""

            calls.append(("get_zone", planet_id, zone_id, user_id))
            return zone

    app.dependency_overrides[get_current_user] = _authenticated(user_id)
    app.dependency_overrides[get_session] = _override_session()
    app.dependency_overrides[planet_controller.get_planet_service] = lambda: FakeService()
    try:
        with TestClient(app) as client:
            responses = [
                client.get(endpoint("/planet")),
                client.get(endpoint(f"/planet/{planet_id}")),
                client.get(endpoint(f"/planet/{planet_id}/zone")),
                client.get(endpoint(f"/planet/{planet_id}/zone/{zone_id}")),
            ]
    finally:
        app.dependency_overrides.clear()

    assert [response.status_code for response in responses] == [200] * 4
    assert responses[0].json()[0]["id"] == str(planet_id)
    assert responses[1].json()["id"] == str(planet_id)
    assert responses[2].json()[0]["planetId"] == str(planet_id)
    assert responses[2].json()[0]["userId"] == str(user_id)
    assert responses[3].json()["id"] == str(zone_id)
    assert calls == [
        ("get_all",),
        ("get_by_id", planet_id),
        ("get_zones_for_planet", planet_id, user_id),
        ("get_zone", planet_id, zone_id, user_id),
    ]


def test_create_planet_zone_forwards_authenticated_user(monkeypatch):
    """Forward the route, payload, and authenticated user to zone creation."""

    user_id = uuid4()
    planet_id = uuid4()
    zone_id = uuid4()
    calls = {}

    async def create_zone(**kwargs):
        """Capture creation arguments and return the created zone."""

        calls.update(kwargs)
        return _zone(zone_id, planet_id, user_id)

    app.dependency_overrides[get_current_user] = _authenticated(user_id)
    app.dependency_overrides[get_session] = _override_session()
    app.dependency_overrides[planet_controller.get_planet_service] = lambda: SimpleNamespace(
        create_zone=create_zone
    )
    try:
        with TestClient(app) as client:
            response = client.post(
                endpoint(f"/planet/{planet_id}/zone"),
                json={"name": "Nea's Place"},
            )
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 201
    assert response.json()["id"] == str(zone_id)
    assert calls == {"planet_id": planet_id, "name": "Nea's Place", "user_id": user_id}


def test_zone_endpoints_require_authentication():
    """Reject zone reads and creation when no current user is available."""

    app.dependency_overrides[planet_controller.get_planet_service] = lambda: SimpleNamespace()
    try:
        with TestClient(app) as client:
            response = client.get(endpoint(f"/planet/{uuid4()}/zone"))
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 401
