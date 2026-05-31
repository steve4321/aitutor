"""Tests for curriculum_agent — session init, next problem, general queries."""
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from app.agents.curriculum_agent import curriculum_node


def _make_state(**overrides) -> dict:
    base = {
        "session_id": str(uuid4()),
        "student_id": str(uuid4()),
        "user_message": "",
        "request_type": "session_init",
        "intent": "manage",
        "subject": "amc_math",
        "student": {"name": "小明", "target_exam": "AMC8"},
        "knowledge_states": [],
        "session_messages": [],
    }
    base.update(overrides)
    return base


def _past_dt(hours_ago: int = 1) -> str:
    return (datetime.now(timezone.utc) - timedelta(hours=hours_ago)).isoformat()


# ── 1–5. Session initialization ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_session_init_with_due_reviews():
    ks = [
        {"knowledge_point_id": str(uuid4()), "mastery": 0.6, "mastery_level": "learning", "next_review": _past_dt()},
    ]
    result = await curriculum_node(_make_state(knowledge_states=ks))

    assert "1 knowledge points due for review" in result["agent_response"]


@pytest.mark.asyncio
async def test_session_init_no_due():
    result = await curriculum_node(_make_state(knowledge_states=[]))

    assert "Welcome" in result["agent_response"]


@pytest.mark.asyncio
async def test_session_init_recommendation_review():
    ks = [
        {"knowledge_point_id": str(uuid4()), "mastery": 0.6, "mastery_level": "learning", "next_review": _past_dt()},
    ]
    result = await curriculum_node(_make_state(knowledge_states=ks))

    assert result["structured_data"]["recommendation"] == "review"


@pytest.mark.asyncio
async def test_session_init_recommendation_learn():
    result = await curriculum_node(_make_state(knowledge_states=[]))

    assert result["structured_data"]["recommendation"] == "learn_new"


@pytest.mark.asyncio
async def test_session_init_weak_areas():
    ks = [
        {"knowledge_point_id": str(uuid4()), "mastery": 0.2, "mastery_level": "novice", "next_review": None},
    ]
    result = await curriculum_node(_make_state(knowledge_states=ks))

    assert "weakest areas" in result["agent_response"].lower() or "weak" in result["agent_response"].lower()


# ── 6–7. Next problem selection ───────────────────────────────────────────


@pytest.mark.asyncio
async def test_next_problem_with_mock():
    fake_problem = SimpleNamespace(
        id=uuid4(),
        question_markdown="Solve for x: 3x = 9",
        difficulty=3,
    )
    mock_db = AsyncMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=False)
    mock_factory = MagicMock(return_value=mock_db)

    with patch("app.agents.curriculum_agent.select_next_problem", return_value=fake_problem), \
         patch("app.db.session.async_session_factory", mock_factory):
        result = await curriculum_node(_make_state(
            intent="practice",
            request_type="chat",
        ))

    assert "3x = 9" in result["agent_response"]
    assert result["structured_data"]["next_problem_id"] == str(fake_problem.id)


@pytest.mark.asyncio
async def test_next_problem_none():
    mock_db = AsyncMock()
    mock_db.__aenter__ = AsyncMock(return_value=mock_db)
    mock_db.__aexit__ = AsyncMock(return_value=False)
    mock_factory = MagicMock(return_value=mock_db)

    with patch("app.agents.curriculum_agent.select_next_problem", return_value=None), \
         patch("app.db.session.async_session_factory", mock_factory):
        result = await curriculum_node(_make_state(
            intent="practice",
            request_type="chat",
        ))

    assert "No more problems" in result["agent_response"]


# ── 8. General query fallback ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_general_no_llm():
    with patch("app.agents.curriculum_agent.is_llm_available", return_value=False):
        result = await curriculum_node(_make_state(
            intent="ask",
            request_type="chat",
            user_message="我的学习进度怎么样",
        ))

    assert "internet connection" in result["agent_response"].lower()
