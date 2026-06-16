"""Application configuration loaded from environment variables."""

from __future__ import annotations

from typing import Literal

from pydantic import model_validator
from pydantic_settings import BaseSettings

_DEFAULT_SECRET = "change-me-in-production"

LLMProviderName = Literal["openai", "deepseek", "minimax", "custom"]

LLM_PROVIDER_PROFILES: dict[str, dict] = {
    "openai": {
        "client": "openai",
        "base_url": None,
        "strong_model": "gpt-4o",
        "fast_model": "gpt-4o-mini",
        "embedding_model": "text-embedding-3-small",
        "api_key_var": "OPENAI_API_KEY",
    },
    "deepseek": {
        "client": "openai",
        "base_url": "https://api.deepseek.com",
        "strong_model": "deepseek-chat",
        "fast_model": "deepseek-chat",
        "embedding_model": None,
        "api_key_var": "OPENAI_API_KEY",
    },
    "minimax": {
        "client": "anthropic",
        "base_url": "https://api.minimaxi.com/anthropic",
        "strong_model": "MiniMax-M3",
        "fast_model": "MiniMax-M3",
        "embedding_model": None,
        "api_key_var": "MINIMAX_API_KEY",
    },
    "custom": {
        "client": "openai",
        "base_url": "",
        "strong_model": "",
        "fast_model": "",
        "embedding_model": "",
        "api_key_var": "OPENAI_API_KEY",
    },
}


class Settings(BaseSettings):
    """Application settings. Values are loaded from .env file or env vars."""

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/aitutor.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    DISABLE_REDIS: bool = False  # Enabled by default; Redis is in docker-compose
    SECRET_KEY: str = _DEFAULT_SECRET
    OPENAI_API_KEY: str = ""
    MINIMAX_API_KEY: str = ""

    ENVIRONMENT: str = "development"
    SENTRY_DSN: str = ""
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1
    SENTRY_PROFILES_SAMPLE_RATE: float = 0.1
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Connection pool (PostgreSQL only; ignored for SQLite)
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE: int = 1800  # seconds

    LLM_PROVIDER: LLMProviderName = "openai"
    LLM_BASE_URL: str = ""
    STRONG_MODEL: str = ""
    FAST_MODEL: str = ""
    EMBEDDING_MODEL: str = ""

    # LLM tuning
    LLM_TIMEOUT: float = 30.0
    LLM_MAX_RETRIES: int = 2
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE_STRONG: float = 0.7
    LLM_TEMPERATURE_FAST: float = 0.1

    # LLM circuit breaker
    LLM_CIRCUIT_FAILURE_THRESHOLD: int = 5
    LLM_CIRCUIT_COOLDOWN_SECONDS: float = 60.0

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    @model_validator(mode="after")
    def _apply_provider_defaults(self) -> "Settings":
        profile = LLM_PROVIDER_PROFILES.get(self.LLM_PROVIDER)
        if profile is None:
            raise ValueError(
                f"Unknown LLM_PROVIDER={self.LLM_PROVIDER!r}. "
                f"Valid: {list(LLM_PROVIDER_PROFILES)}"
            )

        if not self.LLM_BASE_URL and profile.get("base_url"):
            self.LLM_BASE_URL = profile["base_url"]
        if not self.STRONG_MODEL and profile.get("strong_model"):
            self.STRONG_MODEL = profile["strong_model"]
        if not self.FAST_MODEL and profile.get("fast_model"):
            self.FAST_MODEL = profile["fast_model"]
        if not self.EMBEDDING_MODEL and profile.get("embedding_model"):
            self.EMBEDDING_MODEL = profile["embedding_model"]

        key_var = profile.get("api_key_var", "OPENAI_API_KEY")
        provider_key = getattr(self, key_var, "")
        if provider_key:
            self.OPENAI_API_KEY = provider_key

        return self

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
