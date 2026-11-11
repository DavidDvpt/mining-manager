#!/bin/sh
set -eu

cd /opt/docker

. "$HOME/.env.bitwarden"
export BWS_ACCESS_TOKEN BWS_PROJECT_ID
: "${BWS_ACCESS_TOKEN:?BWS_ACCESS_TOKEN manquant}"
: "${BWS_PROJECT_ID:?BWS_PROJECT_ID manquant}"

exec bws run \
  --no-inherit-env \
  --project-id "$BWS_PROJECT_ID" \
  -- "docker compose -p mining-manager -f /opt/docker/mining-manager.yaml down --remove-orphans"
