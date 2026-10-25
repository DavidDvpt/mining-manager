import re
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from copy import deepcopy
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute

from api.api.internal_router import internal_router
from api.api.v1.router import api_v1_router
from api.core.config import get_settings
from api.core.exceptions import register_exception_handlers
from api.core.logging import get_logger, setup_logging

logger = get_logger(__name__)


def generate_operation_id(route: APIRoute) -> str:
    """Generate stable OpenAPI IDs without exposing Python function names."""

    path = re.sub(r"{([^}:]+)(?::[^}]+)?}", r"\1", route.path_format)
    path = re.sub(r"[^a-zA-Z0-9]+", "_", path).strip("_").lower() or "root"
    methods = "_".join(sorted(method.lower() for method in route.methods or ()))
    return f"{methods}_{path}"


def public_openapi_schema(app: FastAPI) -> dict[str, Any]:
    """Return the catalogue-only schema used by the interactive docs."""

    schema = deepcopy(app.openapi())
    schema["paths"] = {
        path: operations
        for path, operations in schema["paths"].items()
        if not any(tag in {"auth", "profile"} for operation in operations.values() for tag in operation.get("tags", []))
    }
    return schema


def build_app() -> FastAPI:
    """Create and configure the FastAPI application."""

    setup_logging()
    settings = get_settings()
    docs_enabled = settings.app_env != "production"

    app = FastAPI(
        title="Mining Manager API",
        version="0.1.0",
        description="Main API for the Mining Manager backend.",
        debug=settings.debug,
        docs_url=None,
        openapi_url=f"{settings.api_v1_prefix}/openapi.json" if docs_enabled else None,
        redoc_url=None,
        generate_unique_id_function=generate_operation_id,
        lifespan=_lifespan,
    )
    register_exception_handlers(app)

    configured_origins = [
        origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()
    ]
    if settings.app_env == "production" and not configured_origins:
        raise ValueError("CORS_ORIGINS must be configured in production")
    if "*" in configured_origins:
        raise ValueError("CORS_ORIGINS cannot contain '*' when credentials are enabled")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=configured_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_v1_router, prefix=settings.api_v1_prefix)
    app.include_router(internal_router, prefix=settings.internal_v1_prefix)

    if docs_enabled:
        docs_openapi_url = f"{settings.api_v1_prefix}/docs/openapi.json"

        @app.get(docs_openapi_url, include_in_schema=False)
        async def docs_openapi() -> JSONResponse:
            return JSONResponse(public_openapi_schema(app))

        @app.get(f"{settings.api_v1_prefix}/docs", include_in_schema=False)
        async def docs() -> Any:
            return get_swagger_ui_html(
                openapi_url=docs_openapi_url,
                title="Mining Manager API - Swagger UI",
            )

        @app.get(f"{settings.api_v1_prefix}/redoc", include_in_schema=False)
        async def redoc() -> Any:
            return get_redoc_html(
                openapi_url=docs_openapi_url,
                title="Mining Manager API - ReDoc",
            )

    @app.get("/health", tags=["health"])
    async def health() -> dict[str, Any]:
        return {"status": "ok"}

    return app


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown hooks."""

    logger.info("mining-manager-api starting up")
    try:
        yield
    finally:
        logger.info("mining-manager-api shutting down")


app = build_app()
