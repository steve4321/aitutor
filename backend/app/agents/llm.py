"""LLM provider factory with graceful degradation and circuit breaker."""
import logging
import time
from enum import Enum
from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic

from app.config import settings, LLM_PROVIDER_PROFILES

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreaker:
    """Track consecutive LLM failures and short-circuit when the provider is down.

    States:
      CLOSED   — calls flow normally; failures increment the counter.
      OPEN     — all calls are rejected immediately (fallback returned).
      HALF_OPEN — one trial call is allowed after the cooldown elapses.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        cooldown_seconds: float = 60.0,
    ) -> None:
        self._failure_threshold = failure_threshold
        self._cooldown_seconds = cooldown_seconds
        self._failure_count = 0
        self._state = CircuitState.CLOSED
        self._opened_at: float | None = None

    @property
    def state(self) -> CircuitState:
        if (
            self._state == CircuitState.OPEN
            and self._opened_at is not None
            and time.monotonic() - self._opened_at >= self._cooldown_seconds
        ):
            self._state = CircuitState.HALF_OPEN
            logger.info("Circuit breaker: OPEN → HALF_OPEN (cooldown elapsed)")
        return self._state

    def allow_call(self) -> bool:
        return self.state != CircuitState.OPEN

    def record_success(self) -> None:
        if self._state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker: HALF_OPEN → CLOSED (trial call succeeded)")
        self._failure_count = 0
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def record_failure(self) -> None:
        self._failure_count += 1
        if self._state == CircuitState.HALF_OPEN:
            self._trip()
            logger.warning(
                "Circuit breaker: HALF_OPEN → OPEN (trial call failed, "
                "cooldown=%.0fs",
                self._cooldown_seconds,
            )
        elif self._failure_count >= self._failure_threshold:
            self._trip()
            logger.warning(
                "Circuit breaker: CLOSED → OPEN (%d consecutive failures, "
                "cooldown=%.0fs)",
                self._failure_count,
                self._cooldown_seconds,
            )

    def reset(self) -> None:
        self._failure_count = 0
        self._state = CircuitState.CLOSED
        self._opened_at = None

    def _trip(self) -> None:
        self._state = CircuitState.OPEN
        self._opened_at = time.monotonic()


llm_circuit_breaker = CircuitBreaker(
    failure_threshold=settings.LLM_CIRCUIT_FAILURE_THRESHOLD,
    cooldown_seconds=settings.LLM_CIRCUIT_COOLDOWN_SECONDS,
)


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
