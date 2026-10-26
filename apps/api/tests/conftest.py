import os
from types import SimpleNamespace
from uuid import uuid4
from urllib.parse import urlsplit

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Keep collection independent from a developer shell that may define DEBUG to a
# non-boolean value (the application settings are imported by the ORM package).
os.environ["DEBUG"] = "false"

TEST_DATABASE_NAME = "entropia_test"


def _test_database_url() -> str:
    """Return the test URL and fail closed if the test environment is unsafe."""

    database_url = os.environ.get("DATABASE_URL")
    if os.environ.get("APP_ENV") != "test" or not database_url:
        raise RuntimeError(
            "Integration tests require APP_ENV=test and an explicit DATABASE_URL."
        )

    parsed = urlsplit(database_url)
    if (
        parsed.scheme != "postgresql+asyncpg"
        or parsed.hostname != "127.0.0.1"
        or parsed.username != "entropia_test"
        or parsed.password != "entropia_test"
        or parsed.path.removeprefix("/") != TEST_DATABASE_NAME
    ):
        raise RuntimeError(
            "Refusing integration tests: DATABASE_URL does not target "
            f"the dedicated {TEST_DATABASE_NAME!r} database."
        )
    return database_url


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(_test_database_url(), pool_pre_ping=True)
    try:
        yield engine
    finally:
        await engine.dispose()


@pytest.fixture
async def test_db_session(test_engine):
    """Provide a transaction-backed session rolled back after each test."""

    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        session_factory = async_sessionmaker(
            bind=connection,
            class_=AsyncSession,
            expire_on_commit=False,
            join_transaction_mode="create_savepoint",
        )
        async with session_factory() as session:
            try:
                yield session
            finally:
                await transaction.rollback()


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
