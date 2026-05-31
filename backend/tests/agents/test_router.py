"""Tests for router_agent.router_node — intent classification and routing."""
import json
from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.messages import AIMessage

from app.agents.router_agent import _rule_based_classify, router_node


def _make_state(**overrides) -> dict:
    """Build a minimal AgentState dict for testing."""
    base = {
        "session_id": "00000000-0000-0000-0000-000000000001",
        "student_id": "00000000-0000-0000-0000-000000000002",
        "user_message": "",
        "request_type": "chat",
    }
    base.update(overrides)
    return base


# ── 1. request_type-based routing ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_attempt_routes_to_assessor():
    state = _make_state(request_type="attempt")
    result = await router_node(state)

    assert result["target_agent"] == "assessor"
    assert result["intent"] == "assess"


# ── 2. session_init routing ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_session_init_routes_to_curriculum():
    state = _make_state(request_type="session_init")
    result = await router_node(state)

    assert result["target_agent"] == "curriculum"
    assert result["intent"] == "manage"


# ── 3–6. keyword-based (rule) routing via _rule_based_classify ─────────────


def test_learn_keyword_tutor():
    result = _rule_based_classify("教我一元二次方程", "chat")
    assert result["intent"] == "learn"
    assert result["target_agent"] == "tutor"


def test_practice_keyword_tutor():
    result = _rule_based_classify("给我提示", "chat")
    assert result["intent"] == "practice"
    assert result["target_agent"] == "tutor"


def test_assess_keyword_assessor():
    result = _rule_based_classify("我写完了", "chat")
    assert result["intent"] == "assess"
    assert result["target_agent"] == "assessor"


def test_manage_keyword_curriculum():
    result = _rule_based_classify("看看我的进度", "chat")
    assert result["intent"] == "manage"
    assert result["target_agent"] == "curriculum"


# ── 7. LLM failure falls back to rules ─────────────────────────────────────


@pytest.mark.asyncio
async def test_llm_failure_fallback_to_rules():
    mock_llm = AsyncMock()
    mock_llm.ainvoke.side_effect = RuntimeError("API timeout")

    with patch("app.agents.router_agent.get_llm", return_value=mock_llm):
        result = await router_node(_make_state(user_message="教我数学"))

    assert result["target_agent"] == "tutor"
    assert result["intent"] == "learn"


# ── 8. No API key uses rules ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_api_key_uses_rules():
    with patch("app.agents.router_agent.get_llm", return_value=None):
        result = await router_node(_make_state(user_message="我想复习"))

    assert result["target_agent"] == "curriculum"
    assert result["intent"] == "manage"


# ── Bonus: LLM returns valid JSON ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_llm_returns_valid_routing():
    llm_response = AIMessage(
        content=json.dumps({
            "intent": "learn",
            "target_agent": "tutor",
            "subject": "chn_poetry",
            "session_mode": "course",
        })
    )
    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=llm_response)

    with patch("app.agents.router_agent.get_llm", return_value=mock_llm):
        result = await router_node(_make_state(user_message="我想学古诗"))

    assert result["intent"] == "learn"
    assert result["subject"] == "chn_poetry"
    assert result["session_mode"] == "course"
