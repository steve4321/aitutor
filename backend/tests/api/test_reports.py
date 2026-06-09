import pytest
from datetime import date, datetime, timedelta, timezone

from app.models.learning import LearningSession


@pytest.mark.asyncio
async def test_daily_report_zeroed(client, auth_headers):
    resp = await client.get("/api/v1/reports/daily", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sessions_count"] == 0
    assert data["problems_attempted"] == 0
    assert data["problems_correct"] == 0
    assert data["xp_earned"] == 0
    assert data["time_spent_minutes"] == 0
    assert data["knowledge_points_reviewed"] == []


@pytest.mark.asyncio
async def test_daily_report_with_sessions(client, auth_headers, student, db_session, knowledge_points):
    today = date.today()
    session = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="math",
        knowledge_point_id=knowledge_points[0].id,
        started_at=datetime.combine(today, datetime.min.time().replace(tzinfo=timezone.utc)),
        xp_earned=50,
        duration_sec=600,
        problems_total=5,
        problems_correct=4,
    )
    db_session.add(session)
    await db_session.flush()

    resp = await client.get("/api/v1/reports/daily", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["sessions_count"] == 1
    assert data["xp_earned"] == 50
    assert data["problems_attempted"] == 5
    assert data["problems_correct"] == 4
    assert data["time_spent_minutes"] == 10
    assert len(data["knowledge_points_reviewed"]) == 1


@pytest.mark.asyncio
async def test_daily_report_with_date_param(client, auth_headers, student, db_session):
    yesterday = date.today() - timedelta(days=1)
    session = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="math",
        started_at=datetime.combine(yesterday, datetime.min.time().replace(tzinfo=timezone.utc)),
        xp_earned=30,
        duration_sec=300,
    )
    db_session.add(session)
    await db_session.flush()

    resp = await client.get(
        f"/api/v1/reports/daily?report_date={yesterday.isoformat()}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["sessions_count"] == 1
    assert data["xp_earned"] == 30


@pytest.mark.asyncio
async def test_daily_report_requires_auth(client):
    resp = await client.get("/api/v1/reports/daily")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_weekly_report_zeroed(client, auth_headers):
    resp = await client.get("/api/v1/reports/weekly", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sessions"] == 0
    assert data["total_problems"] == 0
    assert data["total_correct"] == 0
    assert data["total_xp"] == 0
    assert data["total_time_minutes"] == 0
    assert data["streak_days"] == 0
    assert data["mastery_changes"] == {}


@pytest.mark.asyncio
async def test_weekly_report_streak_days(client, auth_headers, student, db_session):
    from app.models.user import StudentProfile
    from sqlalchemy import select

    result = await db_session.execute(
        select(StudentProfile).where(StudentProfile.user_id == student.id)
    )
    profile = result.scalar_one()
    profile.streak_days = 7
    await db_session.flush()

    resp = await client.get("/api/v1/reports/weekly", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["streak_days"] == 7


@pytest.mark.asyncio
async def test_weekly_report_with_week_start(client, auth_headers, student, db_session):
    week_start = date.today() - timedelta(days=date.today().weekday())
    session = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="math",
        started_at=datetime.combine(week_start, datetime.min.time().replace(tzinfo=timezone.utc)),
        xp_earned=100,
        duration_sec=1200,
    )
    db_session.add(session)
    await db_session.flush()

    resp = await client.get(
        f"/api/v1/reports/weekly?week_start={week_start.isoformat()}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_sessions"] == 1
    assert data["total_xp"] == 100


@pytest.mark.asyncio
async def test_weekly_report_requires_auth(client):
    resp = await client.get("/api/v1/reports/weekly")
    assert resp.status_code in (401, 403)
