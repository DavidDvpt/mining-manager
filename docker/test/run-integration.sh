#!/usr/bin/env bash

set -Eeuo pipefail

compose=(docker compose --project-name mining-manager-test -f docker/test/compose.yaml)
test_port="${PG_TEST_PORT:-5540}"
test_database_url="postgresql+asyncpg://entropia_test:entropia_test@127.0.0.1:${test_port}/entropia_test"

cleanup() {
  status=$?
  "${compose[@]}" down --remove-orphans
  exit "${status}"
}

trap cleanup EXIT

# Keep every command in this process pointed at the test database. In
# particular, do not allow Alembic to fall back to apps/api/alembic.ini.
export APP_ENV=test
export DEBUG=false
export DATABASE_URL="${test_database_url}"
export API_V1_PREFIX=/api/v1
export INTERNAL_V1_PREFIX=/internal/v1
export CORS_ORIGINS=http://localhost:5173

case "${DATABASE_URL}" in
  "postgresql+asyncpg://entropia_test:entropia_test@127.0.0.1:${test_port}/entropia_test") ;;
  *)
    echo "Refusing integration tests: DATABASE_URL is not the dedicated test database." >&2
    exit 1
    ;;
esac

echo "Starting ephemeral PostgreSQL test database..."
"${compose[@]}" up --detach --wait postgres

echo "Applying Alembic migrations to the empty test database..."
(cd apps/api && uv run alembic upgrade head)

echo "Running API integration tests..."
(cd apps/api && uv run pytest tests/integration)
