"""Lesson progress and XP integration tests for /api/v1/lessons/{id}/progress."""
import pytest


@pytest.mark.asyncio
async def test_progress_requires_auth(client, published_course):
    """POST /lessons/{id}/progress without auth returns 401 or 403."""
    resp = await client.post(
        f"/api/v1/lessons/{published_course["lesson_id"]}/progress",
        json={"status": "completed"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_progress_requires_enrollment(client, published_course, auth_headers):
    """POST /lessons/{id}/progress without an active enrollment returns 403."""
    resp = await client.post(
        f"/api/v1/lessons/{published_course["lesson_id"]}/progress",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert resp.status_code == 403
    body = resp.json()
    detail = body.get("detail", body) if isinstance(body, dict) else body
    assert "enroll" in str(detail).lower()


@pytest.mark.asyncio
async def test_progress_completed_awards_xp(
    client, db_session, published_course, student, auth_headers
):
    """Completing a lesson awards 50 XP and returns the new progress percentage."""
    from app.models.enrollment import Enrollment
    from app.models.user import StudentProfile
    from sqlalchemy import select

    enr = Enrollment(
        user_id=student.id,
        course_id=published_course["course_id"],
        is_active=True,
        progress=0,
    )
    db_session.add(enr)
    await db_session.commit()

    initial_xp_result = await db_session.execute(
        select(StudentProfile.xp_total).where(StudentProfile.user_id == student.id)
    )
    initial_xp = initial_xp_result.scalar() or 0

    resp = await client.post(
        f"/api/v1/lessons/{published_course["lesson_id"]}/progress",
        json={"status": "completed"},
        headers=auth_headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["xp_earned"] == 50
    assert data["message"] == "ok"
    assert 0 <= data["progress"] <= 100

    await db_session.refresh(student, attribute_names=["profile"])
    profile = student.profile
    assert profile.xp_total == initial_xp + 50


@pytest.mark.asyncio
async def test_progress_in_progress_no_xp(
    client, db_session, published_course, student, auth_headers
):
    """in_progress status awards no XP and does not update enrollment progress."""
    from app.models.enrollment import Enrollment
    from app.models.user import StudentProfile
    from sqlalchemy import select

    enr = Enrollment(
        user_id=student.id,
        course_id=published_course["course_id"],
        is_active=True,
        progress=0,
    )
    db_session.add(enr)
    await db_session.commit()

    initial_xp_result = await db_session.execute(
        select(StudentProfile.xp_total).where(StudentProfile.user_id == student.id)
    )
    initial_xp = initial_xp_result.scalar() or 0

    resp = await client.post(
        f"/api/v1/lessons/{published_course["lesson_id"]}/progress",
        json={"status": "in_progress"},
        headers=auth_headers,
    )

    assert resp.status_code == 200
    data = resp.json()
    assert data["xp_earned"] == 0

    await db_session.refresh(student, attribute_names=["profile"])
    assert student.profile.xp_total == initial_xp


@pytest.mark.asyncio
async def test_progress_lesson_not_found(client, auth_headers):
    """Random UUID returns 404."""
    from uuid import uuid4

    resp = await client.post(
        f"/api/v1/lessons/{uuid4()}/progress",
        json={"status": "completed"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_lesson_includes_content(client, published_course, auth_headers):
    """GET /lessons/{id} returns the content field so the frontend can render it."""
    resp = await client.get(
        f"/api/v1/lessons/{published_course["lesson_id"]}",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert data["content"] is not None
    assert "objectives" in data["content"]
    assert "summary" in data["content"]
