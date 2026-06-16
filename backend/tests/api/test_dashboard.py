"""Dashboard API endpoint tests: daily-tasks, mastery-summary, streak, summary."""
import pytest
from datetime import date, datetime, timedelta, timezone

from app.models.knowledge import KnowledgePoint
from app.models.learning import KnowledgeState, LearningSession
from app.models.user import StudentProfile
from sqlalchemy import select


# ---------------------------------------------------------------------------
# Daily Tasks
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_daily_tasks_empty(client, auth_headers):
    """GET /dashboard/daily-tasks returns 200 with empty task list for new student."""
    resp = await client.get("/api/v1/dashboard/daily-tasks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["tasks"] == []
    assert data["total_xp_available"] == 0
    assert data["completed_count"] == 0


@pytest.mark.asyncio
async def test_daily_tasks_with_review_due(client, auth_headers, student, db_session, knowledge_points):
    """GET /dashboard/daily-tasks returns review tasks when KS has a due review."""
    now = datetime.now(timezone.utc)

    # Mark a knowledge state as needing review (review_count > 0, next_review <= now)
    ks = KnowledgeState(
        student_id=student.id,
        knowledge_point_id=knowledge_points[0].id,
        mastery=0.6,
        mastery_level="reviewing",
        next_review=now - timedelta(hours=1),
        review_count=2,
        attempts=5,
    )
    db_session.add(ks)
    await db_session.flush()

    resp = await client.get("/api/v1/dashboard/daily-tasks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    review_tasks = [t for t in data["tasks"] if t["type"] == "review"]
    assert len(review_tasks) == 1
    assert review_tasks[0]["knowledge_point_id"] == str(knowledge_points[0].id)
    assert review_tasks[0]["completed"] is False
    assert review_tasks[0]["xp"] == 20
    # The not-yet-completed review contributes to available XP
    assert data["total_xp_available"] > 0


@pytest.mark.asyncio
async def test_daily_tasks_review_completed(client, auth_headers, student, db_session, knowledge_points):
    """GET /dashboard/daily-tasks marks review as completed when a session exists today."""
    now = datetime.now(timezone.utc)
    today = date.today()

    ks = KnowledgeState(
        student_id=student.id,
        knowledge_point_id=knowledge_points[0].id,
        mastery=0.6,
        mastery_level="reviewing",
        next_review=now - timedelta(hours=1),
        review_count=2,
        attempts=5,
    )
    db_session.add(ks)

    # A learning session today on this knowledge point
    session = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="math",
        knowledge_point_id=knowledge_points[0].id,
        started_at=datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc),
        xp_earned=20,
        duration_sec=300,
    )
    db_session.add(session)
    await db_session.flush()

    resp = await client.get("/api/v1/dashboard/daily-tasks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    review_tasks = [t for t in data["tasks"] if t["type"] == "review"]
    assert len(review_tasks) == 1
    assert review_tasks[0]["completed"] is True
    assert data["completed_count"] == 1


@pytest.mark.asyncio
async def test_daily_tasks_with_weak_kp(client, auth_headers, student, db_session, knowledge_points):
    """GET /dashboard/daily-tasks includes practice tasks for weak knowledge points."""
    ks = KnowledgeState(
        student_id=student.id,
        knowledge_point_id=knowledge_points[1].id,
        mastery=0.2,
        mastery_level="not_started",
        attempts=3,
        correct=0,
    )
    db_session.add(ks)
    await db_session.flush()

    resp = await client.get("/api/v1/dashboard/daily-tasks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    practice_tasks = [t for t in data["tasks"] if t["type"] == "practice"]
    assert len(practice_tasks) == 1
    assert practice_tasks[0]["knowledge_point_id"] == str(knowledge_points[1].id)
    assert practice_tasks[0]["xp"] == 30


@pytest.mark.asyncio
async def test_daily_tasks_requires_auth(client):
    resp = await client.get("/api/v1/dashboard/daily-tasks")
    assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Mastery Summary
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_mastery_summary_empty(client, auth_headers):
    """GET /dashboard/mastery-summary returns 200 with no subjects for new student."""
    resp = await client.get("/api/v1/dashboard/mastery-summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["subjects"] == []
    assert data["overall_mastery"] == 0.0


@pytest.mark.asyncio
async def test_mastery_summary_with_data(client, auth_headers, student, db_session):
    """GET /dashboard/mastery-summary groups mastery by pillar."""
    # Create knowledge points with pillars
    kp_algebra = KnowledgePoint(
        code="test.alg.01",
        subject="amc_math",
        name="Test Algebra",
        pillar="Algebra",
    )
    kp_geometry = KnowledgePoint(
        code="test.geo.01",
        subject="amc_math",
        name="Test Geometry",
        pillar="Geometry",
    )
    db_session.add_all([kp_algebra, kp_geometry])
    await db_session.flush()

    ks1 = KnowledgeState(
        student_id=student.id,
        knowledge_point_id=kp_algebra.id,
        mastery=0.8,
    )
    ks2 = KnowledgeState(
        student_id=student.id,
        knowledge_point_id=kp_geometry.id,
        mastery=0.4,
    )
    db_session.add_all([ks1, ks2])
    await db_session.flush()

    resp = await client.get("/api/v1/dashboard/mastery-summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    pillar_names = {s["name"] for s in data["subjects"]}
    assert "Algebra" in pillar_names
    assert "Geometry" in pillar_names
    assert data["overall_mastery"] > 0.0

    for subject in data["subjects"]:
        assert "color" in subject
        assert subject["mastery"] >= 0.0


@pytest.mark.asyncio
async def test_mastery_summary_requires_auth(client):
    resp = await client.get("/api/v1/dashboard/mastery-summary")
    assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Streak
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_streak_zeroed(client, auth_headers):
    """GET /dashboard/streak returns 200 with default values."""
    resp = await client.get("/api/v1/dashboard/streak", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_streak"] == 0
    assert data["longest_streak"] == 0
    assert data["total_xp"] == 0
    assert data["daily_goal_minutes"] == 20
    assert len(data["week_data"]) == 7
    assert all(isinstance(d, bool) for d in data["week_data"])


@pytest.mark.asyncio
async def test_streak_with_profile_data(client, auth_headers, student, db_session):
    """GET /dashboard/streak reflects StudentProfile streak/xp values."""
    result = await db_session.execute(
        select(StudentProfile).where(StudentProfile.user_id == student.id)
    )
    profile = result.scalar_one()
    profile.streak_days = 5
    profile.longest_streak = 10
    profile.xp_total = 500
    profile.daily_goal_minutes = 30
    await db_session.flush()

    resp = await client.get("/api/v1/dashboard/streak", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["current_streak"] == 5
    assert data["longest_streak"] == 10
    assert data["total_xp"] == 500
    assert data["daily_goal_minutes"] == 30


@pytest.mark.asyncio
async def test_streak_week_data_with_sessions(client, auth_headers, student, db_session):
    """GET /dashboard/streak marks days with sufficient session duration."""
    today = date.today()

    # Create a session today long enough to meet half the daily goal (10 min for default 20 min goal)
    session = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="math",
        started_at=datetime.combine(today, datetime.min.time(), tzinfo=timezone.utc),
        duration_sec=900,  # 15 minutes >= 20 * 0.5 = 10 minutes
    )
    db_session.add(session)
    await db_session.flush()

    resp = await client.get("/api/v1/dashboard/streak", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    today_index = today.weekday()
    assert data["week_data"][today_index] is True


@pytest.mark.asyncio
async def test_streak_requires_auth(client):
    resp = await client.get("/api/v1/dashboard/streak")
    assert resp.status_code in (401, 403)


# ---------------------------------------------------------------------------
# Dashboard Summary (aggregated)
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_dashboard_summary(client, auth_headers):
    """GET /dashboard/summary returns all three sections in one response."""
    resp = await client.get("/api/v1/dashboard/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "daily_tasks" in data
    assert "mastery_summary" in data
    assert "streak" in data
    assert data["daily_tasks"]["tasks"] == []
    assert data["mastery_summary"]["overall_mastery"] == 0.0
    assert len(data["streak"]["week_data"]) == 7


@pytest.mark.asyncio
async def test_dashboard_summary_requires_auth(client):
    resp = await client.get("/api/v1/dashboard/summary")
    assert resp.status_code in (401, 403)
