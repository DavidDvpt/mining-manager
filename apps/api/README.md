# API

Main FastAPI application for the Entropia Manager backend.

## Requirements

- Python 3.12 (locked by `.python-version`)
- [uv](https://docs.astral.sh/uv/)

## Installed tools

- FastAPI and Uvicorn
- SQLAlchemy and asyncpg
- Alembic
- Pydantic Settings
- pytest and pytest-asyncio
- Ruff

## Setup

```bash
uv sync --dev
```

The project requires Python `>=3.12` and uses `uv_build` for packaging.
