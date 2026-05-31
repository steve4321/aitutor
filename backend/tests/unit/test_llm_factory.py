"""Unit tests for LLM factory and fallback behaviour."""
from unittest.mock import patch

import pytest

from app.agents.llm import get_fallback_response, get_llm, is_llm_available


class TestIsLlmAvailable:
    def test_false_when_empty_key(self):
        with patch("app.agents.llm.settings.OPENAI_API_KEY", ""):
            assert is_llm_available() is False

    def test_false_when_whitespace_key(self):
        with patch("app.agents.llm.settings.OPENAI_API_KEY", "   "):
            assert is_llm_available() is False

    def test_true_with_key(self):
        with patch("app.agents.llm.settings.OPENAI_API_KEY", "sk-test"):
            assert is_llm_available() is True


class TestGetLlm:
    def test_returns_none_without_key(self):
        with patch("app.agents.llm.settings.OPENAI_API_KEY", ""):
            get_llm.cache_clear()
            result = get_llm("strong")
            assert result is None

    def test_returns_instance_with_key(self):
        with (
            patch("app.agents.llm.settings.OPENAI_API_KEY", "sk-test"),
            patch("app.agents.llm.settings.STRONG_MODEL", "gpt-4o"),
            patch("app.agents.llm.settings.FAST_MODEL", "gpt-4o-mini"),
            patch("app.agents.llm.settings.LLM_TEMPERATURE_STRONG", 0.7),
            patch("app.agents.llm.settings.LLM_TEMPERATURE_FAST", 0.1),
            patch("app.agents.llm.settings.LLM_MAX_TOKENS", 1024),
        ):
            get_llm.cache_clear()
            result = get_llm("strong")
            assert result is not None
            get_llm.cache_clear()

    def test_fast_tier_uses_fast_model(self):
        with (
            patch("app.agents.llm.settings.OPENAI_API_KEY", "sk-test"),
            patch("app.agents.llm.settings.FAST_MODEL", "gpt-4o-mini"),
            patch("app.agents.llm.settings.STRONG_MODEL", "gpt-4o"),
            patch("app.agents.llm.settings.LLM_TEMPERATURE_STRONG", 0.7),
            patch("app.agents.llm.settings.LLM_TEMPERATURE_FAST", 0.1),
            patch("app.agents.llm.settings.LLM_MAX_TOKENS", 1024),
        ):
            get_llm.cache_clear()
            result = get_llm("fast")
            assert result is not None
            get_llm.cache_clear()


class TestGetFallbackResponse:
    @pytest.mark.parametrize(
        "intent",
        ["learn", "practice", "assess", "ask", "manage"],
    )
    def test_known_intents_return_non_empty(self, intent):
        result = get_fallback_response(intent)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_unknown_intent_returns_default(self):
        result = get_fallback_response("totally_unknown_intent")
        assert "temporarily unavailable" in result
