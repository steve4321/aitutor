"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic import model_validator
from pydantic_settings import BaseSettings

_DEFAULT_SECRET = "change-me-in-production"


class Settings(BaseSettings):
    """Application settings. Values are loaded from .env file or env vars."""

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/aitutor.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    DISABLE_REDIS: bool = False  # Enabled by default; Redis is in docker-compose
    SECRET_KEY: str = _DEFAULT_SECRET
    OPENAI_API_KEY: str = ""

    ENVIRONMENT: str = "development"
    SENTRY_DSN: str = ""
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Connection pool (PostgreSQL only; ignored for SQLite)
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800  # seconds

    # LLM tuning
    LLM_TIMEOUT: float = 30.0
    LLM_MAX_RETRIES: int = 2

    # LLM Configuration
    LLM_BASE_URL: str = ""  # DeepSeek: https://api.deepseek.com
    STRONG_MODEL: str = "deepseek-v4-flash"
    FAST_MODEL: str = "deepseek-v4-flash"
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE_STRONG: float = 0.7
    LLM_TEMPERATURE_FAST: float = 0.1

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @model_validator(mode="after")
    def _validate_production_secret(self) -> "Settings":
        if self.ENVIRONMENT == "production" and (
            self.SECRET_KEY == _DEFAULT_SECRET or len(self.SECRET_KEY) < 32
        ):
            raise ValueError(
                "SECRET_KEY must be changed from the default and be at least "
                "32 characters long in production."
            )
        return self


settings = Settings()
