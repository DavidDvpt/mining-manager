#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
ROOT_DIR=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
REMOTE_HOST=${REMOTE_HOST:-ser5}
REMOTE_DIR=${REMOTE_DIR:-/home/davserv/scripts}

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required but not installed." >&2
  exit 1
fi

rsync -av \
  "$ROOT_DIR/scripts/server/mining-manager-start.sh" \
  "$ROOT_DIR/scripts/server/mining-manager-stop.sh" \
  "$REMOTE_HOST:$REMOTE_DIR/"

rsync -av \
  "$ROOT_DIR/docker/prod/mining-manager.compose.prod.yaml" \
  "$REMOTE_HOST:/opt/docker/mining-manager.yaml"

echo "Server scripts copied to $REMOTE_HOST:$REMOTE_DIR"
echo "Production Compose file copied to $REMOTE_HOST:/opt/docker/mining-manager.yaml"
