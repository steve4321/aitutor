"""Enrollment endpoint tests: POST /api/v1/courses/{id}/enroll."""
import pytest


@pytest.mark.asyncio
async def test_enroll_requires_auth(client, published_course):
    """POST /courses/{id}/enroll without auth returns 401 or 403."""
    resp = await client.post(f"/api/v1/courses/{published_course["course_id"]}/enroll")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_enroll_creates_enrollment(client, db_session, published_course, student, auth_headers):
    """First enrollment creates a new Enrollment row with is_active=True and progress=0."""
    from app.models.enrollment import Enrollment
    from sqlalchemy import select

    course_id = published_course["course_id"]
    resp = await client.post(
        f"/api/v1/courses/{course_id}/enroll",
        headers=auth_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["message"] == "Enrolled successfully"
    assert "enrollment_id" in data

    await db_session.commit()
    result = await db_session.execute(
        select(Enrollment).where(
            Enrollment.user_id == student.id,
            Enrollment.course_id == course_id,
        )
    )
    enr = result.scalar_one()
    assert enr.is_active is True
    assert enr.progress == 0


@pytest.mark.asyncio
async def test_enroll_twice_is_idempotent(client, published_course, auth_headers):
    """Enrolling a second time returns 201 with 'Already enrolled' message."""
    course_id = published_course["course_id"]

    first = await client.post(f"/api/v1/courses/{course_id}/enroll", headers=auth_headers)
    assert first.status_code == 201
    assert first.json()["message"] == "Enrolled successfully"

    second = await client.post(f"/api/v1/courses/{course_id}/enroll", headers=auth_headers)
    assert second.status_code == 201
    assert second.json()["message"] == "Already enrolled"
    assert second.json()["enrollment_id"] == first.json()["enrollment_id"]


@pytest.mark.asyncio
async def test_enroll_nonexistent_course_returns_404(client, auth_headers):
    """Enrolling in a random course id returns 404."""
    from uuid import uuid4

    resp = await client.post(
        f"/api/v1/courses/{uuid4()}/enroll",
        headers=auth_headers,
    )
    assert resp.status_code == 404
