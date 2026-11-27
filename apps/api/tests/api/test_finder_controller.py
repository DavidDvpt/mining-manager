from datetime import UTC, datetime
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from api.api.deps import get_current_user
from api.core.config import get_settings
from api.db import get_session
from api.db.models import LotType
from api.main import app


@pytest.mark.parametrize("endpoint", ["finders", "finder-amplifiers", "excavators"])
def test_available_tool_lots_are_scoped_and_grouped(item_data, monkeypatch, endpoint):
    """Verify each tool inventory returns owned lots by model ID with TT and catalogue data."""

    user_id = uuid4()
    item, economy, _ = item_data
    item.finder = SimpleNamespace(
        is_limited=True, use_per_minute=12, depth=Decimal("250"), range=None, ammo_burn=10
    )
    item.finder_amplifier = SimpleNamespace(
        is_limited=True, efficiency=Decimal("5"), profession_level_min=None
    )
    item.excavator = SimpleNamespace(
        is_limited=True, efficiency=Decimal("5"), use_per_minute=12
    )
    economy.avg_mu_percent = None
    economy.avg_mu_plus = None
    lots = [
        SimpleNamespace(
            id=uuid4(),
            user_id=user_id,
            type=LotType.TRANSACTION,
            origin=SimpleNamespace(item_id=item.id),
            qty=1,
            reserved=0,
            tool_lot=SimpleNamespace(tier=tier, tt=Decimal(tt), is_default=False),
            created_at=datetime.now(UTC),
            updated_at=None,
            is_active=True,
        )
        for tier, tt in [(2, "9.5"), (4, "15")]
    ]
    catalogue_result = MagicMock()
    catalogue_result.all.return_value = [item]
    lot_result = MagicMock()
    lot_result.unique.return_value.all.return_value = lots
    session = AsyncMock()
    session.scalars.side_effect = [catalogue_result, lot_result]

    async def fake_session():
        """Use the existing repository and service with a simulated DB result."""

        yield session

    async def fake_current_user():
        """Authenticate as the tool lot owner."""

        return {"id": user_id, "role": "USER", "pseudo": "tool-owner"}

    monkeypatch.setitem(app.dependency_overrides, get_session, fake_session)
    monkeypatch.setitem(app.dependency_overrides, get_current_user, fake_current_user)
    with TestClient(app) as client:
        response = client.get(f"{get_settings().api_v1_prefix}/{endpoint}/lots")

    assert response.status_code == 200
    inventory = response.json()
    assert set(inventory) == {str(item.id)}
    owned_lots = inventory[str(item.id)]
    assert [(lot["id"], lot["tier"], lot["tt"]) for lot in owned_lots] == [
        (str(lots[0].id), 2, "9.5"),
        (str(lots[1].id), 4, "15"),
    ]
    details = owned_lots[0]["item"]["details"]
    if endpoint == "finders":
        assert details["depth"] == "250"
        assert details["ammoBurn"] == 10
    else:
        assert details["efficiency"] == "5"
    if endpoint == "excavators":
        assert details["usePerMinute"] == 12
    assert owned_lots[0]["item"]["economy"]["decay"] == "2"
    query = session.scalars.await_args_list[1].args[0]
    assert set(query.compile().params["item_id_1"]) == {item.id}
    assert query.compile().params["user_id_1"] == user_id
    assert "lot.is_active IS true" in str(query)
    assert "lot.qty - lot.reserved" in str(query)
