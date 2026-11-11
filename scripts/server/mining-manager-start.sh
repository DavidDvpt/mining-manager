#!/bin/sh
set -eu

cd /opt/docker

IMAGE_TAG=${1:-${IMAGE_TAG:-latest}}
DOCKERHUB_NAMESPACE=${DOCKERHUB_NAMESPACE:-lamouche42}
. "$HOME/.env.bitwarden"

export BWS_ACCESS_TOKEN BWS_PROJECT_ID
: "${BWS_ACCESS_TOKEN:?BWS_ACCESS_TOKEN manquant}"
: "${BWS_PROJECT_ID:?BWS_PROJECT_ID manquant}"

exec bws run \
  --no-inherit-env \
  --project-id "$BWS_PROJECT_ID" \
  -- "IMAGE_TAG=$IMAGE_TAG DOCKERHUB_NAMESPACE=$DOCKERHUB_NAMESPACE docker compose -p mining-manager -f /opt/docker/mining-manager.yaml pull && IMAGE_TAG=$IMAGE_TAG DOCKERHUB_NAMESPACE=$DOCKERHUB_NAMESPACE docker compose -p mining-manager -f /opt/docker/mining-manager.yaml up -d"
