"""Orchestrator node integration tests: loads student context from DB."""
import pytest
from datetime import datetime, timezone
from uuid import uuid4

from app.agents.orchestrator import orchestrator_node
from app.models.learning import LearningSession
from app.models.message import Message


@pytest.mark.asyncio
async def test_loads_student_context(db_session, student):
    """orchestrator_node loads student name, grade_level, target_exam."""
    await db_session.commit()

    result = await orchestrator_node(
        {"student_id": student.id, "session_id": None, "db_session": db_session}
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

    result = await orchestrator_node(
        {"student_id": student.id, "session_id": session.id, "db_session": db_session}
    )

    messages = result["session_messages"]
    assert len(messages) >= 1
    assert messages[0]["content"] == "你好老师"
    assert messages[0]["role"] == "user"


@pytest.mark.asyncio
async def test_loads_problem_data(db_session, student, knowledge_points, mcq_problem):
    """orchestrator_node returns problem_data with question_markdown and correct_answer."""
    await db_session.commit()

    result = await orchestrator_node(
        {
            "student_id": student.id,
            "session_id": None,
            "problem_id": mcq_problem.id,
            "db_session": db_session,
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

    random_id = uuid4()
    result = await orchestrator_node(
        {"student_id": random_id, "session_id": None, "db_session": db_session}
    )

    assert result["student"]["student_id"] == random_id
    assert "name" not in result["student"] or result["student"].get("name") is None


@pytest.mark.asyncio
async def test_handles_no_problem_id(db_session, student):
    """When problem_id is omitted, no problem_data key appears in result."""
    await db_session.commit()

    result = await orchestrator_node(
        {"student_id": student.id, "session_id": None, "db_session": db_session}
    )

    assert "problem_data" not in result
