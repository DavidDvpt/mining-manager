"""JWT access and refresh token helpers."""

import time
from typing import Any

import jwt


def _seconds(value: str) -> int:
    units = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return int(value[:-1]) * units[value[-1].lower()] if value[-1].lower() in units else int(value)


def sign_token(*, secret: str, claims: dict[str, Any], expires_in: str) -> str:
    now = int(time.time())
    return jwt.encode({**claims, "iat": now, "exp": now + _seconds(expires_in)}, secret, algorithm="HS256")


def decode_token(*, secret: str, token: str) -> dict[str, Any]:
    return jwt.decode(token, secret, algorithms=["HS256"])


def max_age(expires_in: str) -> int:
    return _seconds(expires_in)
