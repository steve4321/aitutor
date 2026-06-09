import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.models.learning import LearningSession
from app.models.user import StudentProfile
from app.services.report_service import aggregate_sessions, get_streak_days


@pytest.mark.asyncio
async def test_aggregate_sessions_returns_zeroed_dict_when_no_sessions(db_session, student):
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end = datetime(2025, 12, 31, tzinfo=timezone.utc)
    result = await aggregate_sessions(db_session, student.id, start, end)
    assert result == {
        "total_sessions": 0,
        "total_xp": 0,
        "total_time_minutes": 0,
        "total_problems": 0,
        "total_correct": 0,
    }


@pytest.mark.asyncio
async def test_aggregate_sessions_sums_multiple_sessions(db_session, student):
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end = datetime(2025, 12, 31, tzinfo=timezone.utc)
    t = datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc)

    s1 = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="amc_math",
        started_at=t,
        duration_sec=600,
        xp_earned=50,
        problems_total=10,
        problems_correct=8,
    )
    s2 = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="amc_math",
        started_at=t + timedelta(hours=1),
        duration_sec=1200,
        xp_earned=100,
        problems_total=20,
        problems_correct=15,
    )
    db_session.add_all([s1, s2])
    await db_session.flush()

    result = await aggregate_sessions(db_session, student.id, start, end)
    assert result["total_sessions"] == 2
    assert result["total_xp"] == 150
    assert result["total_time_minutes"] == 30
    assert result["total_problems"] == 30
    assert result["total_correct"] == 23


@pytest.mark.asyncio
async def test_aggregate_sessions_only_counts_within_date_range(db_session, student):
    t1 = datetime(2025, 1, 15, tzinfo=timezone.utc)
    t2 = datetime(2025, 6, 15, tzinfo=timezone.utc)
    start = datetime(2025, 3, 1, tzinfo=timezone.utc)
    end = datetime(2025, 9, 1, tzinfo=timezone.utc)

    s_outside = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="amc_math",
        started_at=t1,
        duration_sec=300,
        xp_earned=20,
        problems_total=5,
        problems_correct=3,
    )
    s_inside = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="amc_math",
        started_at=t2,
        duration_sec=600,
        xp_earned=40,
        problems_total=10,
        problems_correct=7,
    )
    db_session.add_all([s_outside, s_inside])
    await db_session.flush()

    result = await aggregate_sessions(db_session, student.id, start, end)
    assert result["total_sessions"] == 1
    assert result["total_xp"] == 40
    assert result["total_problems"] == 10


@pytest.mark.asyncio
async def test_aggregate_sessions_only_counts_given_student(db_session, student):
    start = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end = datetime(2025, 12, 31, tzinfo=timezone.utc)
    t = datetime(2025, 6, 1, 12, 0, tzinfo=timezone.utc)

    other_user_id = uuid4()
    s_other = LearningSession(
        student_id=other_user_id,
        session_type="practice",
        subject="amc_math",
        started_at=t,
        duration_sec=600,
        xp_earned=100,
        problems_total=10,
        problems_correct=10,
    )
    s_mine = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="amc_math",
        started_at=t,
        duration_sec=300,
        xp_earned=30,
        problems_total=5,
        problems_correct=4,
    )
    db_session.add_all([s_other, s_mine])
    await db_session.flush()

    result = await aggregate_sessions(db_session, student.id, start, end)
    assert result["total_sessions"] == 1
    assert result["total_xp"] == 30
    assert result["total_problems"] == 5


@pytest.mark.asyncio
async def test_get_streak_days_returns_streak_from_profile(db_session, student):
    from sqlalchemy import select

    result = await db_session.execute(
        select(StudentProfile).where(StudentProfile.user_id == student.id)
    )
    profile = result.scalar_one()
    profile.streak_days = 7
    await db_session.flush()

    streak = await get_streak_days(db_session, student.id)
    assert streak == 7


@pytest.mark.asyncio
async def test_get_streak_days_returns_zero_when_no_profile(db_session):
    random_id = uuid4()
    streak = await get_streak_days(db_session, random_id)
    assert streak == 0
