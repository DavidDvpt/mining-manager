#!/bin/sh
set -eu

ROOT_DIR=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
NAMESPACE=${DOCKERHUB_NAMESPACE:-lamouche42}
TAG=${IMAGE_TAG:-$(node -p "require('$ROOT_DIR/package.json').version")}
PLATFORM=${PLATFORM:-linux/amd64}

if ! command -v docker >/dev/null 2>&1; then
  echo "Docker is required but not installed." >&2
  exit 1
fi

docker buildx build --platform "$PLATFORM" --push \
  -t "$NAMESPACE/mining-manager-api:$TAG" \
  -t "$NAMESPACE/mining-manager-api:latest" \
  -f "$ROOT_DIR/apps/api/Dockerfile.prod" \
  "$ROOT_DIR/apps/api"

docker buildx build --platform "$PLATFORM" --push \
  -t "$NAMESPACE/mining-manager-frontend:$TAG" \
  -t "$NAMESPACE/mining-manager-frontend:latest" \
  -f "$ROOT_DIR/apps/client/Dockerfile.prod" \
  "$ROOT_DIR"

echo "Published $NAMESPACE/mining-manager-api:$TAG"
echo "Published $NAMESPACE/mining-manager-frontend:$TAG"

sh "$ROOT_DIR/scripts/copy-server-scripts.sh"
