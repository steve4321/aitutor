"""LLM provider factory with graceful degradation."""
import logging
from functools import lru_cache

from langchain_openai import ChatOpenAI
from app.config import settings

logger = logging.getLogger(__name__)


def is_llm_available() -> bool:
    """Check if OpenAI API key is configured."""
    return bool(settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip())


@lru_cache(maxsize=2)
def get_llm(tier: str = "strong") -> ChatOpenAI | None:
    """
    Get a cached LLM instance.
    
    Args:
        tier: "strong" (GPT-4o for teaching/assessment) or 
              "fast" (GPT-4o-mini for routing/classification)
    
    Returns:
        ChatOpenAI instance or None if no API key configured.
    """
    if not is_llm_available():
        logger.warning("OPENAI_API_KEY not set — AI features disabled")
        return None

    model_map = {
        "strong": settings.STRONG_MODEL,
        "fast": settings.FAST_MODEL,
    }
    model = model_map.get(tier, settings.STRONG_MODEL)

    return ChatOpenAI(
        model=model,
        api_key=settings.OPENAI_API_KEY,
        temperature=settings.LLM_TEMPERATURE_STRONG if tier == "strong" else settings.LLM_TEMPERATURE_FAST,
        max_tokens=settings.LLM_MAX_TOKENS,
    )


def get_fallback_response(intent: str) -> str:
    """Return a canned response when LLM is unavailable."""
    fallbacks = {
        "learn": "AI tutoring is temporarily unavailable. Please try again in a few minutes!",
        "practice": "Practice mode is temporarily unavailable. You can still browse problems.",
        "assess": "Scoring is temporarily unavailable. Your answer has been recorded.",
        "ask": "I can't answer questions right now, but I'll be back soon!",
        "manage": "This feature requires an internet connection.",
    }
    return fallbacks.get(intent, "AI features are temporarily unavailable.")
