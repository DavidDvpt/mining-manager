"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Any, Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration shared by the application factory and its adapters."""

    model_config = SettingsConfigDict(
        env_file=(".env", "apps/api/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    debug: bool
    database_url: str
    api_v1_prefix: str
    internal_v1_prefix: str
    cors_origins: str
    jwt_access_secret: str = "change_me_dev_access_secret"
    jwt_refresh_secret: str = "change_me_dev_refresh_secret"
    jwt_access_expires_in: str = "24h"
    jwt_refresh_access_expires_in: str = "1h"
    jwt_refresh_expires_in: str = "7d"
    internal_api_token: str = ""


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""

    settings_type: Any = Settings
    return settings_type()
