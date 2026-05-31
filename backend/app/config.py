"""Application configuration loaded from environment variables."""

from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings. Values are loaded from .env file or env vars."""

    DATABASE_URL: str = "sqlite+aiosqlite:///./data/aitutor.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    DISABLE_REDIS: bool = True  # Set False when Redis is available
    SECRET_KEY: str = "change-me-in-production"
    OPENAI_API_KEY: str = ""
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # LLM Configuration
    STRONG_MODEL: str = "gpt-4o"
    FAST_MODEL: str = "gpt-4o-mini"
    LLM_MAX_TOKENS: int = 1024
    LLM_TEMPERATURE_STRONG: float = 0.7
    LLM_TEMPERATURE_FAST: float = 0.1

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
