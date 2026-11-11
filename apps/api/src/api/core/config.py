"""Application settings loaded from environment variables."""

from functools import lru_cache
from typing import Any, Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    """Configuration shared by the application factory and its adapters."""

    model_config = SettingsConfigDict(
        env_file=(".env", "apps/api/.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: Literal["development", "test", "production"] = "development"
    debug: bool
    database_url: str = ""
    db_scheme: str = "postgresql+asyncpg"
    db_host: str = ""
    db_port: int = 5432
    db_name: str = ""
    db_user: str = ""
    db_password: str = ""
    api_v1_prefix: str
    internal_v1_prefix: str
    cors_origins: str
    jwt_access_secret: str = "change_me_dev_access_secret"
    jwt_refresh_secret: str = "change_me_dev_refresh_secret"
    jwt_access_expires_in: str = "24h"
    jwt_refresh_access_expires_in: str = "1h"
    jwt_refresh_expires_in: str = "7d"
    internal_api_token: str = ""

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        """Build the database URL from component settings when no URL is supplied."""

        if self.database_url:
            return self
        required_values = {
            "DB_HOST": self.db_host,
            "DB_NAME": self.db_name,
            "DB_USER": self.db_user,
            "DB_PASSWORD": self.db_password,
        }
        missing = [name for name, value in required_values.items() if not value]
        if missing:
            raise ValueError(f"Database configuration is incomplete: {', '.join(missing)}")
        self.database_url = URL.create(
            drivername=self.db_scheme,
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
        ).render_as_string(hide_password=False)
        return self


@lru_cache
def get_settings() -> Settings:
    """Return the cached application settings instance."""

    settings_type: Any = Settings
    return settings_type()
