"""LLM provider factory with graceful degradation."""
import logging
from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic

from app.config import settings, LLM_PROVIDER_PROFILES

logger = logging.getLogger(__name__)


def is_llm_available() -> bool:
    return bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())


@lru_cache(maxsize=2)
def get_llm(tier: str = "strong") -> ChatOpenAI | ChatAnthropic | None:
    if not is_llm_available():
        logger.warning(
            "LLM API key not set (provider=%s) — AI features disabled",
            settings.LLM_PROVIDER,
        )
        return None

    model_map = {
        "strong": settings.STRONG_MODEL,
        "fast": settings.FAST_MODEL,
    }
    model = model_map.get(tier, settings.STRONG_MODEL)
    if not model:
        logger.error("No model configured for tier=%s provider=%s", tier, settings.LLM_PROVIDER)
        return None

    profile = LLM_PROVIDER_PROFILES.get(settings.LLM_PROVIDER, {})
    client_type = profile.get("client", "openai")
    temperature = settings.LLM_TEMPERATURE_STRONG if tier == "strong" else settings.LLM_TEMPERATURE_FAST

    if client_type == "anthropic":
        kwargs: dict = {
            "model": model,
            "api_key": settings.OPENAI_API_KEY,
            "temperature": temperature,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "timeout": settings.LLM_TIMEOUT,
            "max_retries": settings.LLM_MAX_RETRIES,
        }
        if settings.LLM_BASE_URL:
            kwargs["base_url"] = settings.LLM_BASE_URL
        return ChatAnthropic(**kwargs)

    kwargs = {
        "model": model,
        "api_key": settings.OPENAI_API_KEY,
        "temperature": temperature,
        "max_tokens": settings.LLM_MAX_TOKENS,
        "timeout": settings.LLM_TIMEOUT,
        "max_retries": settings.LLM_MAX_RETRIES,
    }
    if settings.LLM_BASE_URL:
        kwargs["base_url"] = settings.LLM_BASE_URL

    return ChatOpenAI(**kwargs)


@lru_cache(maxsize=1)
def get_embedding_model() -> OpenAIEmbeddings | None:
    if not is_llm_available():
        return None
    if not settings.EMBEDDING_MODEL:
        return None

    kwargs: dict = {
        "api_key": settings.OPENAI_API_KEY,
        "model": settings.EMBEDDING_MODEL,
    }
    if settings.LLM_BASE_URL:
        kwargs["base_url"] = settings.LLM_BASE_URL

    try:
        return OpenAIEmbeddings(**kwargs)
    except Exception:
        logger.warning("Failed to initialize embedding model", exc_info=True)
        return None


def get_fallback_response(intent: str) -> str:
    fallbacks = {
        "learn": "AI tutoring is temporarily unavailable. Please try again in a few minutes!",
        "practice": "Practice mode is temporarily unavailable. You can still browse problems.",
        "assess": "Scoring is temporarily unavailable. Your answer has been recorded.",
        "ask": "I can't answer questions right now, but I'll be back soon!",
        "manage": "This feature requires an internet connection.",
    }
    return fallbacks.get(intent, "AI features are temporarily unavailable.")
