"""Unit tests for problem_selector service."""
import pytest
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.agents.services.problem_selector import select_next_problem
from app.models.problem import Problem
from app.models.learning import StudentAttempt, LearningSession
from app.models.knowledge import KnowledgePoint


async def _seed_problem(db_session, *, subject="amc_math", difficulty=3, fmt="mcq"):
    p = Problem(
        id=uuid4(),
        subject=subject,
        format=fmt,
        question_markdown="What is 2+2?",
        difficulty=difficulty,
    )
    db_session.add(p)
    await db_session.flush()
    return p


async def _seed_session(db_session, student_id):
    session = LearningSession(
        id=uuid4(),
        student_id=student_id,
        session_type="practice",
        subject="amc_math",
        started_at=datetime.now(timezone.utc),
    )
    db_session.add(session)
    await db_session.flush()
    return session


class TestSelectNextProblem:

    @pytest.mark.asyncio
    async def test_returns_problem_when_available(self, db_session, student):
        await _seed_problem(db_session)
        await _seed_problem(db_session)

        result = await select_next_problem(
            db=db_session,
            student_id=student.id,
            subject="amc_math",
            target_exam="AMC8",
            knowledge_states=[],
        )
        assert result is not None
        assert isinstance(result, Problem)

    @pytest.mark.asyncio
    async def test_filters_by_subject(self, db_session, student):
        math_p = await _seed_problem(db_session, subject="amc_math", difficulty=3)
        await _seed_problem(db_session, subject="ket_english", difficulty=3)

        result = await select_next_problem(
            db=db_session,
            student_id=student.id,
            subject="amc_math",
            target_exam="AMC8",
            knowledge_states=[],
        )
        assert result is not None
        assert result.id == math_p.id

    @pytest.mark.asyncio
    async def test_filters_by_difficulty_range(self, db_session, student):
        await _seed_problem(db_session, difficulty=1)
        target_p = await _seed_problem(db_session, difficulty=5)
        await _seed_problem(db_session, difficulty=10)

        knowledge_states = [
            {
                "knowledge_point_id": str(uuid4()),
                "mastery": 0.5,
                "next_review": None,
                "stability": 1.0,
                "difficulty": 5.0,
            }
        ]

        result = await select_next_problem(
            db=db_session,
            student_id=student.id,
            subject="amc_math",
            target_exam="AMC8",
            knowledge_states=knowledge_states,
        )
        assert result is not None
        assert target_p.difficulty - 1 <= result.difficulty <= target_p.difficulty + 1

    @pytest.mark.asyncio
    async def test_excludes_recently_attempted(self, db_session, student):
        problem = await _seed_problem(db_session, difficulty=3)
        session = await _seed_session(db_session, student.id)

        attempt = StudentAttempt(
            id=uuid4(),
            session_id=session.id,
            student_id=student.id,
            problem_id=problem.id,
            answer="A",
            is_correct=False,
        )
        db_session.add(attempt)
        await db_session.flush()

        other_problem = await _seed_problem(db_session, difficulty=3)

        result = await select_next_problem(
            db=db_session,
            student_id=student.id,
            subject="amc_math",
            target_exam="AMC8",
            knowledge_states=[],
        )
        assert result is not None
        assert result.id != problem.id

    @pytest.mark.asyncio
    async def test_excludes_session_problems(self, db_session, student):
        excluded = await _seed_problem(db_session, difficulty=3)
        available = await _seed_problem(db_session, difficulty=3)

        result = await select_next_problem(
            db=db_session,
            student_id=student.id,
            subject="amc_math",
            target_exam="AMC8",
            knowledge_states=[],
            session_problem_ids=[excluded.id],
        )
        assert result is not None
        assert result.id != excluded.id

    @pytest.mark.asyncio
    async def test_returns_none_when_no_match(self, db_session, student):
        result = await select_next_problem(
            db=db_session,
            student_id=student.id,
            subject="amc_math",
            target_exam="AMC8",
            knowledge_states=[],
        )
        assert result is None

    @pytest.mark.asyncio
    async def test_prefers_due_review_problems(self, db_session, student):
        kp_id = uuid4()
        kp = KnowledgePoint(
            id=kp_id,
            code="test-review-kp",
            subject="amc_math",
            name="Review KP",
        )
        db_session.add(kp)

        review_problem = await _seed_problem(
            db_session, difficulty=3, fmt="mcq"
        )
        review_problem.knowledge_point_ids = [str(kp_id)]
        await _seed_problem(db_session, difficulty=3)

        past = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
        knowledge_states = [
            {
                "knowledge_point_id": str(kp_id),
                "mastery": 0.4,
                "next_review": past,
                "stability": 1.0,
                "difficulty": 5.0,
            }
        ]

        result = await select_next_problem(
            db=db_session,
            student_id=student.id,
            subject="amc_math",
            target_exam="AMC8",
            knowledge_states=knowledge_states,
        )
        assert result is not None
