"""Unit tests for knowledge_tracker service."""
import pytest
from uuid import uuid4

from app.agents.services.knowledge_tracker import (
    update_mastery,
    apply_knowledge_updates,
)
from app.agents.services.fsrs import classify_mastery_level
from app.models.learning import KnowledgeState, StudentAttempt
from app.models.knowledge import KnowledgePoint
from app.models.problem import Problem
from app.models.user import User


# ---------------------------------------------------------------------------
# Part A: Pure function tests (no DB)
# ---------------------------------------------------------------------------


class TestUpdateMastery:
    """Tests for the pure update_mastery function."""

    def test_correct_increases_mastery(self):
        result = update_mastery(
            current_mastery=0.5,
            is_correct=True,
            difficulty=5.0,
        )
        assert result > 0.5

    def test_wrong_decreases_mastery(self):
        result = update_mastery(
            current_mastery=0.5,
            is_correct=False,
            difficulty=5.0,
        )
        assert result < 0.5

    def test_upper_bound_1(self):
        result = update_mastery(
            current_mastery=0.99,
            is_correct=True,
            difficulty=5.0,
        )
        assert result <= 1.0

    def test_lower_bound_0(self):
        result = update_mastery(
            current_mastery=0.01,
            is_correct=False,
            difficulty=5.0,
        )
        assert result >= 0.0

    def test_hint_penalty_reduces_gain(self):
        result_no_hint = update_mastery(
            current_mastery=0.5,
            is_correct=True,
            difficulty=5.0,
            hint_level=0,
        )
        result_with_hint = update_mastery(
            current_mastery=0.5,
            is_correct=True,
            difficulty=5.0,
            hint_level=2,
        )
        assert result_with_hint < result_no_hint

    def test_high_difficulty_bonus(self):
        result_easy = update_mastery(
            current_mastery=0.5,
            is_correct=True,
            difficulty=5.0,
            problem_difficulty=3,
        )
        result_hard = update_mastery(
            current_mastery=0.5,
            is_correct=True,
            difficulty=5.0,
            problem_difficulty=8,
        )
        assert result_hard > result_easy

    def test_zero_hint_no_penalty(self):
        result = update_mastery(
            current_mastery=0.5,
            is_correct=True,
            difficulty=5.0,
            hint_level=0,
        )
        # With hint_level=0 the penalty term is 0*0.05 = 0
        alpha = 0.3
        expected = 0.5 + alpha * (1.0 - 0.5)
        assert abs(result - expected) < 1e-9


# ---------------------------------------------------------------------------
# Part B: DB integration tests
# ---------------------------------------------------------------------------
# These tests rely on conftest.py fixtures: db_session (AsyncSession) and
# student (User).  If the conftest is not yet available the tests will fail
# at collection time but the code remains correct.


@pytest.fixture
def kp_id():
    """Return a fresh UUID to use as a knowledge point id."""
    return uuid4()


async def _seed_knowledge_point(db_session, kp_id):
    """Insert a KnowledgePoint row so the FK constraint is satisfied."""
    kp = KnowledgePoint(
        id=kp_id,
        code=f"test-kp-{kp_id.hex[:8]}",
        subject="amc_math",
        name="Test Knowledge Point",
    )
    db_session.add(kp)
    await db_session.flush()
    return kp


class TestApplyKnowledgeUpdates:
    """Tests for apply_knowledge_updates (requires DB)."""

    @pytest.mark.asyncio
    async def test_creates_new_knowledge_state(self, db_session, student, kp_id):
        await _seed_knowledge_point(db_session, kp_id)

        updates = [
            {
                "knowledge_point_id": str(kp_id),
                "is_correct": True,
                "hint_level_used": 0,
            }
        ]
        await apply_knowledge_updates(db_session, student.id, updates)
        await db_session.flush()

        from sqlalchemy import select

        result = await db_session.execute(
            select(KnowledgeState).where(
                KnowledgeState.student_id == student.id,
                KnowledgeState.knowledge_point_id == kp_id,
            )
        )
        state = result.scalar_one()
        assert state.mastery > 0.0
        assert state.mastery_level != "not_started"
        assert state.review_count == 1

    @pytest.mark.asyncio
    async def test_updates_existing_state(self, db_session, student, kp_id):
        await _seed_knowledge_point(db_session, kp_id)

        existing = KnowledgeState(
            student_id=student.id,
            knowledge_point_id=kp_id,
            mastery=0.3,
            mastery_level="attempted",
            difficulty=5.0,
            stability=1.0,
            retrievability=0.9,
        )
        db_session.add(existing)
        await db_session.flush()

        updates = [
            {
                "knowledge_point_id": str(kp_id),
                "is_correct": True,
                "hint_level_used": 0,
            }
        ]
        await apply_knowledge_updates(db_session, student.id, updates)
        await db_session.flush()

        await db_session.refresh(existing)
        assert existing.mastery > 0.3
        assert existing.stability > 0.0

    @pytest.mark.asyncio
    async def test_increments_review_count(self, db_session, student, kp_id):
        await _seed_knowledge_point(db_session, kp_id)

        updates = [
            {
                "knowledge_point_id": str(kp_id),
                "is_correct": True,
                "hint_level_used": 0,
            }
        ]
        await apply_knowledge_updates(db_session, student.id, updates)
        await db_session.flush()

        from sqlalchemy import select

        result = await db_session.execute(
            select(KnowledgeState).where(
                KnowledgeState.student_id == student.id,
                KnowledgeState.knowledge_point_id == kp_id,
            )
        )
        state = result.scalar_one()
        assert state.review_count == 1

    @pytest.mark.asyncio
    async def test_correct_increments_correct_count(self, db_session, student, kp_id):
        await _seed_knowledge_point(db_session, kp_id)

        updates = [
            {
                "knowledge_point_id": str(kp_id),
                "is_correct": True,
                "hint_level_used": 0,
            }
        ]
        await apply_knowledge_updates(db_session, student.id, updates)
        await db_session.flush()

        from sqlalchemy import select

        result = await db_session.execute(
            select(KnowledgeState).where(
                KnowledgeState.student_id == student.id,
                KnowledgeState.knowledge_point_id == kp_id,
            )
        )
        state = result.scalar_one()
        assert state.correct == 1
        assert state.lapse_count == 0

    @pytest.mark.asyncio
    async def test_wrong_increments_lapse_count(self, db_session, student, kp_id):
        await _seed_knowledge_point(db_session, kp_id)

        updates = [
            {
                "knowledge_point_id": str(kp_id),
                "is_correct": False,
                "hint_level_used": 0,
            }
        ]
        await apply_knowledge_updates(db_session, student.id, updates)
        await db_session.flush()

        from sqlalchemy import select

        result = await db_session.execute(
            select(KnowledgeState).where(
                KnowledgeState.student_id == student.id,
                KnowledgeState.knowledge_point_id == kp_id,
            )
        )
        state = result.scalar_one()
        assert state.lapse_count == 1
        assert state.correct == 0

    @pytest.mark.asyncio
    async def test_mastery_level_updated(self, db_session, student, kp_id):
        await _seed_knowledge_point(db_session, kp_id)

        updates = [
            {
                "knowledge_point_id": str(kp_id),
                "is_correct": True,
                "hint_level_used": 0,
            }
        ]
        await apply_knowledge_updates(db_session, student.id, updates)
        await db_session.flush()

        from sqlalchemy import select

        result = await db_session.execute(
            select(KnowledgeState).where(
                KnowledgeState.student_id == student.id,
                KnowledgeState.knowledge_point_id == kp_id,
            )
        )
        state = result.scalar_one()
        expected_level = classify_mastery_level(state.mastery)
        assert state.mastery_level == expected_level
