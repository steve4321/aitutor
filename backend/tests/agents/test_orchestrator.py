"""Orchestrator node integration tests: loads student context from DB."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.agents.orchestrator import orchestrator_node
from app.models.learning import LearningSession
from app.models.message import Message


def _make_session_factory(db_session):
    mock_factory = MagicMock()
    mock_factory.return_value.__aenter__ = AsyncMock(return_value=db_session)
    mock_factory.return_value.__aexit__ = AsyncMock(return_value=False)
    return mock_factory


@pytest.mark.asyncio
async def test_loads_student_context(db_session, student):
    """orchestrator_node loads student name, grade_level, target_exam."""
    await db_session.commit()

    session_factory = _make_session_factory(db_session)
    with patch("app.agents.orchestrator.async_session_factory", session_factory):
        result = await orchestrator_node(
            {"student_id": student.id, "session_id": None}
        )

    assert result["student"]["name"] == "测试小明"
    assert result["student"]["grade_level"] == 5
    assert result["student"]["target_exam"] == "AMC8"


@pytest.mark.asyncio
async def test_loads_session_messages(db_session, student):
    """orchestrator_node returns session_messages for a session with messages."""
    session = LearningSession(
        student_id=student.id,
        session_type="chat",
        subject="general",
        started_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add(session)
    await db_session.flush()

    msg = Message(
        session_id=session.id,
        role="user",
        content="你好老师",
    )
    db_session.add(msg)
    await db_session.commit()

    session_factory = _make_session_factory(db_session)
    with patch("app.agents.orchestrator.async_session_factory", session_factory):
        result = await orchestrator_node(
            {"student_id": student.id, "session_id": session.id}
        )

    messages = result["session_messages"]
    assert len(messages) >= 1
    assert messages[0]["content"] == "你好老师"
    assert messages[0]["role"] == "user"


@pytest.mark.asyncio
async def test_loads_problem_data(db_session, student, knowledge_points, mcq_problem):
    """orchestrator_node returns problem_data with question_markdown and correct_answer."""
    await db_session.commit()

    session_factory = _make_session_factory(db_session)
    with patch("app.agents.orchestrator.async_session_factory", session_factory):
        result = await orchestrator_node(
            {
                "student_id": student.id,
                "session_id": None,
                "problem_id": mcq_problem.id,
            }
        )

    problem_data = result["problem_data"]
    assert problem_data is not None
    assert "question_markdown" in problem_data
    assert problem_data["correct_answer"] == "B"


@pytest.mark.asyncio
async def test_handles_invalid_student_gracefully(db_session):
    """Passing a non-existent student_id returns minimal dict without crashing."""
    await db_session.commit()

    session_factory = _make_session_factory(db_session)
    random_id = uuid4()
    with patch("app.agents.orchestrator.async_session_factory", session_factory):
        result = await orchestrator_node(
            {"student_id": random_id, "session_id": None}
        )

    assert result["student"]["student_id"] == random_id
    assert "name" not in result["student"] or result["student"].get("name") is None


@pytest.mark.asyncio
async def test_handles_no_problem_id(db_session, student):
    """When problem_id is omitted, no problem_data key appears in result."""
    await db_session.commit()

    session_factory = _make_session_factory(db_session)
    with patch("app.agents.orchestrator.async_session_factory", session_factory):
        result = await orchestrator_node(
            {"student_id": student.id, "session_id": None}
        )

    assert "problem_data" not in result
