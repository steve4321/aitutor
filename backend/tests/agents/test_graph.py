"""Full graph integration tests: run_agent() through the compiled LangGraph."""
import pytest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from langchain_core.messages import AIMessage


def _mock_llm_response(content: str = "这是AI老师的回复"):
    """Return an AsyncMock LLM whose ainvoke returns an AIMessage."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(return_value=AIMessage(content=content))
    return mock_llm


# ---------------------------------------------------------------------------
# 1. Chat flow with mock LLM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_chat_flow_with_mock_llm(
    db_session, student, knowledge_points, mcq_problem
):
    """run_agent with request_type='chat' routes through orchestrator → router → tutor → response."""
    await db_session.commit()

    mock_llm = _mock_llm_response("数学很有趣！让我们来学习方程。")

    def _get_llm_side_effect(tier: str = "strong"):
        return mock_llm

    with (
        patch("app.agents.router_agent.get_llm", side_effect=_get_llm_side_effect),
        patch("app.agents.tutor_agent.get_llm", side_effect=_get_llm_side_effect),
        patch("app.agents.llm.is_llm_available", return_value=True),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="你好，教我数学",
            request_type="chat",
            db_session=db_session,
        )

    assert "agent_response" in result
    assert result["agent_response"]  # non-empty
    assert result["error"] is None


# ---------------------------------------------------------------------------
# 2. MCQ correct — no LLM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attempt_mcq_correct_no_llm(
    db_session, student, knowledge_points, mcq_problem
):
    """MCQ exact-match: correct answer yields is_correct=True without LLM."""
    await db_session.commit()

    with (
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="B",
            request_type="attempt",
            problem_id=mcq_problem.id,
            student_answer="B",
            db_session=db_session,
        )

    structured = result.get("structured_data") or {}
    assert structured.get("is_correct") is True


# ---------------------------------------------------------------------------
# 3. MCQ wrong — no LLM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_attempt_mcq_wrong_no_llm(
    db_session, student, knowledge_points, mcq_problem
):
    """MCQ exact-match: wrong answer yields is_correct=False."""
    await db_session.commit()

    with (
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="A",
            request_type="attempt",
            problem_id=mcq_problem.id,
            student_answer="A",
            db_session=db_session,
        )

    structured = result.get("structured_data") or {}
    assert structured.get("is_correct") is False


# ---------------------------------------------------------------------------
# 4. Session init — no LLM
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_session_init_no_llm(
    db_session, student, knowledge_points
):
    """session_init routes to curriculum agent and returns a recommendation."""
    await db_session.commit()

    with (
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="开始学习",
            request_type="session_init",
            db_session=db_session,
        )

    assert "agent_response" in result
    assert result["agent_response"]  # non-empty recommendation


# ---------------------------------------------------------------------------
# 5. Degraded mode — all fallbacks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_graph_degraded_all_fallbacks(
    db_session, student, knowledge_points, mcq_problem
):
    """No LLM at all: chat returns fallback text, MCQ still scores correctly."""
    await db_session.commit()

    # --- chat fallback ---
    with (
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        chat_result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="告诉我关于数学的知识",
            request_type="chat",
            db_session=db_session,
        )

    assert "unavailable" in chat_result["agent_response"].lower() or chat_result["agent_response"]

    # --- MCQ still works ---
    with (
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        attempt_result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="B",
            request_type="attempt",
            problem_id=mcq_problem.id,
            student_answer="B",
            db_session=db_session,
        )

    structured = attempt_result.get("structured_data") or {}
    assert structured.get("is_correct") is True
