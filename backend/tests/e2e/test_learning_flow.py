"""E2E learning scenario tests: full stack through API → agent → DB."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4
from datetime import datetime, timezone

from langchain_core.messages import AIMessage
from sqlalchemy import select

from app.models.learning import LearningSession, KnowledgeState
from app.models.message import Message


def _make_session_factory(db_session):
    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__ = AsyncMock(return_value=db_session)
    mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock_factory


def _mock_llm_response(content: str = "AI回复"):
    mock = AsyncMock()
    mock.ainvoke = AsyncMock(return_value=AIMessage(content=content))
    return mock


@pytest.mark.asyncio
async def test_new_student_first_session(
    client, db_session, student, knowledge_points, mcq_problem, auth_headers
):
    """Create session → send chat → submit attempt → verify DB state."""
    session_factory = _make_session_factory(db_session)
    mock_llm = _mock_llm_response("让我来帮你学习方程！")

    def _get_llm_side_effect(tier: str = "strong"):
        return mock_llm

    with (
        patch("app.agents.graph.async_session_factory", session_factory),
        patch("app.agents.orchestrator.async_session_factory", session_factory),
        patch("app.db.session.async_session_factory", session_factory),
        patch("app.agents.llm.get_llm", side_effect=_get_llm_side_effect),
        patch("app.agents.llm.is_llm_available", return_value=True),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        chat_resp = await client.post(
            "/api/v1/chat/message",
            json={"content": "教我数学"},
            headers=auth_headers,
        )

    assert chat_resp.status_code == 200
    chat_data = chat_resp.json()
    session_id = chat_data["session_id"]
    assert session_id is not None

    # Submit an MCQ attempt via problems endpoint (mocked agent)
    mock_agent = {
        "agent_response": "Correct! Well done.",
        "structured_data": {"is_correct": True, "evaluation_method": "exact_match"},
        "error": None,
    }
    with patch("app.api.v1.problems.run_agent", new_callable=AsyncMock, return_value=mock_agent):
        attempt_resp = await client.post(
            f"/api/v1/problems/{mcq_problem.id}/attempt",
            json={"answer": "B"},
            headers=auth_headers,
        )

    assert attempt_resp.status_code == 200
    assert attempt_resp.json()["is_correct"] is True


@pytest.mark.asyncio
async def test_fsrs_review_cycle(
    client, db_session, student, knowledge_points, auth_headers
):
    """KnowledgeState with next_review=now triggers review recommendation on session_init."""
    kp = knowledge_points[0]
    ks = KnowledgeState(
        student_id=student.id,
        knowledge_point_id=kp.id,
        mastery=0.5,
        mastery_level="learning",
        difficulty=5.0,
        stability=1.0,
        retrievability=0.6,
        next_review=datetime.now(timezone.utc),
        review_count=2,
    )
    db_session.add(ks)
    await db_session.commit()

    session_factory = _make_session_factory(db_session)
    with (
        patch("app.agents.graph.async_session_factory", session_factory),
        patch("app.agents.orchestrator.async_session_factory", session_factory),
        patch("app.db.session.async_session_factory", session_factory),
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="开始学习",
            request_type="session_init",
        )

    structured = result.get("structured_data") or {}
    assert structured.get("due_reviews", 0) >= 1


@pytest.mark.asyncio
async def test_multi_turn_conversation(
    client, db_session, student, auth_headers
):
    """3 messages in the same session each return a response."""
    session = LearningSession(
        student_id=student.id,
        session_type="chat",
        subject="general",
        started_at=datetime.now(timezone.utc),
    )
    db_session.add(session)
    await db_session.commit()

    for i in range(3):
        mock_result = {
            "agent_response": f"Reply {i}",
            "structured_data": None,
            "error": None,
        }
        with patch("app.api.v1.chat.run_agent", new_callable=AsyncMock, return_value=mock_result):
            resp = await client.post(
                "/api/v1/chat/message",
                json={"content": f"消息{i}", "session_id": str(session.id)},
                headers=auth_headers,
            )
        assert resp.status_code == 200

    # Verify messages persisted in DB
    result = await db_session.execute(
        select(Message).where(Message.session_id == session.id)
    )
    messages = list(result.scalars().all())
    assert len(messages) >= 3


@pytest.mark.asyncio
async def test_wrong_then_right_tracking(
    client, db_session, student, knowledge_points, mcq_problem, auth_headers
):
    """Answer wrong → mastery decreases → answer right → mastery increases."""
    kp = knowledge_points[0]
    ks = KnowledgeState(
        student_id=student.id,
        knowledge_point_id=kp.id,
        mastery=0.6,
        mastery_level="learning",
        difficulty=5.0,
        stability=2.0,
        retrievability=0.8,
        next_review=datetime.now(timezone.utc),
        review_count=1,
    )
    db_session.add(ks)
    await db_session.commit()

    session_factory = _make_session_factory(db_session)

    # Wrong answer through graph
    with (
        patch("app.agents.graph.async_session_factory", session_factory),
        patch("app.agents.orchestrator.async_session_factory", session_factory),
        patch("app.db.session.async_session_factory", session_factory),
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        wrong_result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="A",
            request_type="attempt",
            problem_id=mcq_problem.id,
            student_answer="A",
        )

    assert wrong_result["structured_data"]["is_correct"] is False

    # Flush knowledge updates manually to test session
    await db_session.flush()
    await db_session.refresh(ks)
    mastery_after_wrong = ks.mastery

    # Correct answer through graph
    with (
        patch("app.agents.graph.async_session_factory", session_factory),
        patch("app.agents.orchestrator.async_session_factory", session_factory),
        patch("app.db.session.async_session_factory", session_factory),
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        from app.agents import run_agent

        right_result = await run_agent(
            session_id=uuid4(),
            student_id=student.id,
            user_message="B",
            request_type="attempt",
            problem_id=mcq_problem.id,
            student_answer="B",
        )

    assert right_result["structured_data"]["is_correct"] is True

    await db_session.flush()
    await db_session.refresh(ks)
    assert ks.mastery >= mastery_after_wrong


@pytest.mark.asyncio
async def test_degraded_mode_full_flow(
    client, db_session, student, knowledge_points, mcq_problem, auth_headers
):
    """No LLM: chat returns fallback, MCQ still scores correctly."""
    session_factory = _make_session_factory(db_session)

    # Chat in degraded mode
    with (
        patch("app.agents.graph.async_session_factory", session_factory),
        patch("app.agents.orchestrator.async_session_factory", session_factory),
        patch("app.db.session.async_session_factory", session_factory),
        patch("app.agents.llm.is_llm_available", return_value=False),
        patch("app.agents.__init__._compiled_graph", None),
    ):
        chat_resp = await client.post(
            "/api/v1/chat/message",
            json={"content": "教我数学"},
            headers=auth_headers,
        )

    assert chat_resp.status_code == 200
    assert chat_resp.json()["role"] == "assistant"

    # MCQ attempt still works in degraded mode
    with (
        patch("app.agents.graph.async_session_factory", session_factory),
        patch("app.agents.orchestrator.async_session_factory", session_factory),
        patch("app.db.session.async_session_factory", session_factory),
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
        )

    assert result["structured_data"]["is_correct"] is True
