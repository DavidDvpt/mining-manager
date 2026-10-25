import os
from types import SimpleNamespace
from uuid import uuid4

import pytest

# Keep collection independent from a developer shell that may define DEBUG to a
# non-boolean value (the application settings are imported by the ORM package).
os.environ["DEBUG"] = "false"


@pytest.fixture
def item_data():
    item_id = uuid4()
    economy = SimpleNamespace(tt=1, decay=2)
    details = SimpleNamespace(efficiency=3)
    item = SimpleNamespace(
        id=item_id,
        name="Test item",
        img_id=10,
        nexus_id=20,
        weight=1.5,
        is_untradeable=False,
        is_rare=True,
        is_active=True,
        nexus_url="https://example.test/item",
        description="A test item",
        created_at=None,
        updated_at=None,
        economy=economy,
    )
    return item, economy, details
