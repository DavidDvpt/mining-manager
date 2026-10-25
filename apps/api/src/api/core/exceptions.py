"""Application exceptions and FastAPI error handlers.

All API errors use the legacy response contract::

    {"message": "..."}

Validation errors additionally include an ``errors`` array.  In particular,
the API never exposes FastAPI's default ``detail`` key.
"""

from __future__ import annotations

import logging
from typing import cast

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, NoResultFound

logger = logging.getLogger(__name__)


class AppError(Exception):
    """Safe, expected application error with an HTTP status code."""

    def __init__(
        self,
        status_code: int = 500,
        message: str = "Internal server error",
    ) -> None:
        self.status_code = status_code
        self.message = message
        super().__init__(message)


def is_unique_violation(exc: IntegrityError) -> bool:
    """Return whether an integrity error is a PostgreSQL unique violation."""

    original = exc.orig
    return getattr(original, "sqlstate", None) == "23505" or getattr(
        original, "pgcode", None
    ) == "23505"


def _message_response(message: str, status_code: int) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"message": message})


def _validation_errors(exc: RequestValidationError) -> list[dict[str, str]]:
    errors: list[dict[str, str]] = []
    for error in exc.errors():
        location = error.get("loc", ())
        path = ".".join(str(part) for part in location if part != "body")
        errors.append(
            {
                "path": path,
                "code": str(error.get("type", "validation_error")),
                "message": str(error.get("msg", "Invalid value")),
            }
        )
    return errors


async def _validation_error_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    validation_error = cast(RequestValidationError, exc)
    return JSONResponse(
        status_code=422,
        content={
            "message": "Invalid request",
            "errors": _validation_errors(validation_error),
        },
    )


async def _app_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    app_error = cast(AppError, exc)
    if not 400 <= app_error.status_code < 600:
        return _message_response("Internal server error", 500)
    message = (
        app_error.message
        if app_error.status_code != 500
        else "Internal server error"
    )
    return _message_response(message, app_error.status_code)


async def _integrity_error_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    integrity_error = cast(IntegrityError, exc)
    if is_unique_violation(integrity_error):
        return _message_response("Resource already exists", 409)
    return _message_response("Internal server error", 500)


async def _no_result_found_handler(
    _request: Request, _exc: Exception
) -> JSONResponse:
    return _message_response("Resource not found", 404)


async def _generic_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error: %s", exc)
    return _message_response("Internal server error", 500)


def register_exception_handlers(app: FastAPI) -> None:
    """Register the API's exception-to-response mapping on ``app``."""

    app.add_exception_handler(AppError, _app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, _validation_error_handler)
    app.add_exception_handler(IntegrityError, _integrity_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(NoResultFound, _no_result_found_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _generic_error_handler)


__all__ = [
    "AppError",
    "is_unique_violation",
    "register_exception_handlers",
]
