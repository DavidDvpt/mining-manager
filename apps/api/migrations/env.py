import asyncio
import os
from logging.config import fileConfig

from alembic import context
from api.db import Base
from sqlalchemy import Connection, pool
from sqlalchemy.engine import URL
from sqlalchemy.ext.asyncio import async_engine_from_config

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

def get_database_url() -> str | None:
    """Return the database URL from the environment or the local Alembic fallback.

    ``DATABASE_URL`` has priority when explicitly provided. Otherwise, the
    component-based ``DB_*`` variables used by the API and production Compose
    configuration are assembled into a PostgreSQL URL. A missing component is
    reported before Alembic attempts to connect.
    """

    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    component_names = (
        "DB_SCHEME",
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD",
    )
    components = {name: os.getenv(name) for name in component_names}
    missing = [name for name, value in components.items() if not value]
    if missing:
        return None

    db_scheme = components["DB_SCHEME"]
    db_host = components["DB_HOST"]
    db_port = components["DB_PORT"]
    db_name = components["DB_NAME"]
    db_user = components["DB_USER"]
    db_password = components["DB_PASSWORD"]
    assert db_scheme is not None
    assert db_host is not None
    assert db_port is not None
    assert db_name is not None
    assert db_user is not None
    assert db_password is not None

    return URL.create(
        drivername=db_scheme,
        username=db_user,
        password=db_password,
        host=db_host,
        port=int(db_port),
        database=db_name,
    ).render_as_string(hide_password=False)


# Prefer the environment (Docker/API configuration) and keep a local fallback
# in alembic.ini for commands run directly from apps/api.
database_url = get_database_url()
if database_url:
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import all model modules here as they are added so their tables are
# registered on Base.metadata before Alembic runs autogenerate.
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
