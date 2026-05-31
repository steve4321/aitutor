"""Tests for tutor_agent — subject/mode prompt selection, history handling, fallback."""
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage

from app.agents.tutor_agent import tutor_node


def _make_state(**overrides) -> dict:
    base = {
        "session_id": str(uuid4()),
        "student_id": str(uuid4()),
        "user_message": "帮我理解这个概念",
        "request_type": "chat",
        "subject": "amc_math",
        "session_mode": "practice",
        "intent": "learn",
        "student": {"name": "小明", "grade_level": 5, "target_exam": "AMC8"},
        "session_messages": [],
        "knowledge_states": [],
        "hint_level": 0,
    }
    base.update(overrides)
    return base


def _mock_llm_available(response_text: str = "AI response"):
    ai_msg = AIMessage(content=response_text)
    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=ai_msg)
    return mock_llm


# ── 1. No LLM fallback ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_no_llm_returns_fallback():
    with patch("app.agents.tutor_agent.is_llm_available", return_value=False):
        result = await tutor_node(_make_state())

    assert result["model_used"] == "none"
    assert "unavailable" in result["agent_response"].lower() or result["agent_response"]


# ── 2–5. Prompt selection by (subject, session_mode) ──────────────────────


@pytest.mark.asyncio
async def test_math_practice_uses_socratic():
    mock_llm = _mock_llm_available()
    with patch("app.agents.tutor_agent.is_llm_available", return_value=True), \
         patch("app.agents.tutor_agent.get_llm", return_value=mock_llm):
        result = await tutor_node(_make_state(subject="amc_math", session_mode="practice"))

    assert result["model_used"] == "strong"
    mock_llm.ainvoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_math_course_uses_course_prompt():
    mock_llm = _mock_llm_available()
    with patch("app.agents.tutor_agent.is_llm_available", return_value=True), \
         patch("app.agents.tutor_agent.get_llm", return_value=mock_llm):
        await tutor_node(_make_state(subject="amc_math", session_mode="course"))

    call_args = mock_llm.ainvoke.call_args[0][0]
    system_msg = call_args[0].content
    assert len(system_msg) > 0


@pytest.mark.asyncio
async def test_poetry_course_uses_teaching():
    mock_llm = _mock_llm_available()
    with patch("app.agents.tutor_agent.is_llm_available", return_value=True), \
         patch("app.agents.tutor_agent.get_llm", return_value=mock_llm):
        await tutor_node(_make_state(subject="chn_poetry", session_mode="course"))

    mock_llm.ainvoke.assert_awaited_once()


@pytest.mark.asyncio
async def test_default_is_socratic():
    mock_llm = _mock_llm_available()
    with patch("app.agents.tutor_agent.is_llm_available", return_value=True), \
         patch("app.agents.tutor_agent.get_llm", return_value=mock_llm):
        result = await tutor_node(_make_state(subject="unknown", session_mode="unknown"))

    assert result["model_used"] == "strong"


# ── 6–7. Conversation history handling ────────────────────────────────────


@pytest.mark.asyncio
async def test_includes_conversation_history():
    messages = [
        {"role": "user", "content": "msg1"},
        {"role": "assistant", "content": "msg2"},
        {"role": "user", "content": "msg3"},
    ]
    mock_llm = _mock_llm_available()
    with patch("app.agents.tutor_agent.is_llm_available", return_value=True), \
         patch("app.agents.tutor_agent.get_llm", return_value=mock_llm):
        await tutor_node(_make_state(session_messages=messages))

    called_messages = mock_llm.ainvoke.call_args[0][0]
    user_msgs = [m for m in called_messages if m.type == "human"]
    assert len(user_msgs) == 3  # 2 user from history + 1 current


@pytest.mark.asyncio
async def test_history_limited_to_10():
    messages = [{"role": "user" if i % 2 == 0 else "assistant", "content": f"msg{i}"} for i in range(15)]
    mock_llm = _mock_llm_available()
    with patch("app.agents.tutor_agent.is_llm_available", return_value=True), \
         patch("app.agents.tutor_agent.get_llm", return_value=mock_llm):
        await tutor_node(_make_state(session_messages=messages))

    called_messages = mock_llm.ainvoke.call_args[0][0]
    history_msgs = called_messages[1:-1]  # exclude system + current user message
    assert len(history_msgs) == 10
