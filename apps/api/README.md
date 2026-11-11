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

## Préparer PostgreSQL en production

Les exemples ci-dessous utilisent uniquement des noms génériques. Remplace
`app_db`, `app_user`, `db_admin` et `dump_role` par les valeurs du serveur,
sans publier les mots de passe.

Se connecter à PostgreSQL avec un compte administrateur :

```bash
psql -U db_admin -d postgres
```

Afficher les bases et les utilisateurs :

```sql
\\l
\\du
```

Créer la base sans donner sa propriété au compte applicatif :

```sql
CREATE DATABASE app_db OWNER db_admin;
```

Se connecter à la base et donner au compte applicatif les droits nécessaires
aux migrations :

```sql
\\c app_db

GRANT CONNECT ON DATABASE app_db TO app_user;
GRANT USAGE, CREATE ON SCHEMA public TO app_user;
```

Vérifier les droits du compte applicatif :

```sql
SELECT
  has_database_privilege('app_user', 'app_db', 'CONNECT') AS can_connect,
  has_database_privilege('app_user', 'app_db', 'CREATE') AS can_create,
  has_database_privilege('app_user', 'app_db', 'TEMPORARY') AS can_use_temporary;

SELECT
  has_schema_privilege('app_user', 'public', 'USAGE') AS can_use_schema,
  has_schema_privilege('app_user', 'public', 'CREATE') AS can_create_in_schema;

SELECT *
FROM information_schema.role_table_grants
WHERE grantee = 'app_user';

\\dp
```

Créer ou vérifier un rôle de sauvegarde en lecture seule :

```sql
GRANT CONNECT ON DATABASE app_db TO dump_role;
GRANT pg_read_all_data TO dump_role;
\\du+ dump_role
```

Tester une sauvegarde avec ce rôle :

```bash
pg_dump -U dump_role -d app_db > app_db.sql
```

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

Pour annuler la dernière migration :

```bash
npm exec nx run api:alembic:downgrade
```

Cette commande recule toutes les révisions Alembic jusqu’à `base` sur la base configurée dans
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
