from uuid import uuid4

import httpx

from api.api.deps import get_current_user
from api.core.config import get_settings
from api.db import get_session
from api.db.models import Planet, User
from api.main import app


def endpoint(path: str) -> str:
    """Build an API v1 endpoint path for the integration test."""

    return f"{get_settings().api_v1_prefix}{path}"


async def _create_user(test_db_session, prefix: str) -> User:
    """Create and flush a database user for an endpoint scenario."""

    user = User(pseudo=f"planet-{prefix}-{uuid4().hex[:10]}", password_hash="hash")
    test_db_session.add(user)
    await test_db_session.flush()
    return user


async def test_planet_zone_endpoints_persist_and_isolate_zones(test_db_session):
    """Persist a zone and expose it only to its authenticated owner."""

    owner = await _create_user(test_db_session, "owner")
    other_user = await _create_user(test_db_session, "other")
    planet = Planet(name=f"Integration planet {uuid4()}")
    test_db_session.add(planet)
    await test_db_session.flush()

    async def override_session():
        """Use the transaction-backed integration test session."""

        yield test_db_session

    async def owner_user():
        """Authenticate the zone owner for the request."""

        return {"id": owner.id, "role": "USER", "pseudo": owner.pseudo}

    async def other_user_dependency():
        """Authenticate a different user for isolation checks."""

        return {"id": other_user.id, "role": "USER", "pseudo": other_user.pseudo}

    app.dependency_overrides[get_session] = override_session
    app.dependency_overrides[get_current_user] = owner_user
    try:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            planet_response = await client.get(endpoint(f"/planet/{planet.id}"))
            create_response = await client.post(
                endpoint(f"/planet/{planet.id}/zone"),
                json={"name": "Owned zone"},
            )
            zone_id = create_response.json()["id"]
            owner_zones = await client.get(
                endpoint(f"/planet/{planet.id}/zone")
            )
            owner_zone = await client.get(
                endpoint(f"/planet/{planet.id}/zone/{zone_id}")
            )

        app.dependency_overrides[get_current_user] = other_user_dependency
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            other_zones = await client.get(
                endpoint(f"/planet/{planet.id}/zone")
            )
            hidden_zone = await client.get(
                endpoint(f"/planet/{planet.id}/zone/{zone_id}")
            )
    finally:
        app.dependency_overrides.clear()

    assert planet_response.status_code == 200
    assert create_response.status_code == 201
    assert create_response.json()["userId"] == str(owner.id)
    assert owner_zones.status_code == 200
    assert len(owner_zones.json()) == 1
    assert owner_zone.status_code == 200
    assert other_zones.status_code == 200
    assert other_zones.json() == []
    assert hidden_zone.status_code == 404
