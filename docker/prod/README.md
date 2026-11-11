# Production deployment

This stack deploys only `api` and `frontend` on the existing external
`ser5-network`. PostgreSQL, Redis, n8n and the reverse proxy remain managed by
the production infrastructure.

## Build and publish

Authenticate to Docker Hub, then build and publish a versioned release:

```sh
docker login
IMAGE_TAG=0.1.0 DOCKERHUB_NAMESPACE=lamouche42 ./scripts/docker-build-prod.sh
```

If `IMAGE_TAG` is omitted, the script reads the version from the root
`package.json`. Each image receives both the version tag and `latest`.

After both pushes succeed, the build script synchronizes the two server
control scripts to `ser5:/home/davserv/scripts/` and the production Compose
file to `/opt/docker/mining-manager.yaml` using `rsync` over SSH. The copied
scripts are made executable.

The script creates locally:

- `lamouche42/mining-manager-api:0.1.0`
- `lamouche42/mining-manager-frontend:0.1.0`

## Bitwarden on the server

Use the same server convention as the reference application. Create
`$HOME/.env.bitwarden` with only:

```sh
BWS_ACCESS_TOKEN=...
BWS_PROJECT_ID=...
```

The Bitwarden project must provide these runtime secret names:

- `DB_SCHEME`
- `DB_HOST`
- `DB_PORT`
- `DB_NAME_MM`
- `DB_USER_MM`
- `DB_PASSWORD`
- `JWT_ACCESS_SECRET`
- `JWT_REFRESH_SECRET` (optional)
- `INTERNAL_API_TOKEN` (optional)

`CORS_ORIGINS`, `IMAGE_TAG` and `DOCKERHUB_NAMESPACE` are non-secret Compose
configuration. They can be exported in the server shell or set in the command
environment; the compose defaults the namespace to `lamouche42` and the tag to
`latest`.

The build script installs `docker/prod/mining-manager.compose.prod.yaml` as
`/opt/docker/mining-manager.yaml`. Make sure `ser5-network` already exists,
then start it with:

```sh
~/scripts/mining-manager-start.sh 0.1.0
```

The start script runs `docker compose pull` under `bws run`, then starts the
migrations job and application services. To stop the stack:

```sh
~/scripts/mining-manager-stop.sh
```

The API is exposed to the existing proxy as `api:8040`, and the frontend as
`frontend:8039` on `ser5-network`.
