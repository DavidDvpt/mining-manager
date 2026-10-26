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

Synchronise les dépendances de l’API, y compris les dépendances de développement
comme pytest et Ruff.

The project requires Python `>=3.12` and uses `uv_build` for packaging.

## Commandes

Les commandes Nx suivantes se lancent depuis la racine du repository :

```bash
npm exec nx run api:test
```

Lance tous les tests de l’API avec pytest. La cible exécute `uv run pytest`
depuis le dossier `apps/api`.

```bash
npm exec nx run api:test-integration
```

Lance les tests d’intégration avec un PostgreSQL dédié et éphémère. La commande
démarre le container PostgreSQL en `tmpfs`, attend son healthcheck, applique les
migrations Alembic sur une base vide, exécute les tests, puis arrête et supprime
le container et le réseau de test. Elle doit être lancée depuis la racine du
repository et ne touche pas à la base de développement.

```bash
npm exec nx run api:alembic:upgrade
```

Applique toutes les migrations Alembic jusqu’à la dernière version (`head`).
Cette commande met à jour le schéma PostgreSQL configuré dans
`apps/api/.env`.

Depuis le dossier `apps/api`, les commandes équivalentes sont :

```bash
uv run pytest
```

Exécute directement la suite de tests Python définie dans `tests/`.

```bash
uv run ruff check src tests
```

Vérifie le style et les erreurs statiques dans le code source et les tests.

```bash
uv run alembic upgrade head
```

Exécute directement les migrations de base de données jusqu’à la révision la
plus récente. La cible Nx `api:alembic:upgrade` est recommandée depuis la
racine du repository.
