import pytest
from uuid import uuid4


@pytest.mark.asyncio
async def test_create_session(client, auth_headers):
    resp = await client.post(
        "/api/v1/sessions",
        json={"session_type": "practice", "subject": "math"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["session_type"] == "practice"
    assert data["subject"] == "math"
    assert data["xp_earned"] == 0


@pytest.mark.asyncio
async def test_create_session_with_knowledge_point(client, auth_headers, knowledge_points):
    kp_id = knowledge_points[0].id
    resp = await client.post(
        "/api/v1/sessions",
        json={
            "session_type": "lesson",
            "subject": "math",
            "knowledge_point_id": str(kp_id),
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["knowledge_point_id"] == str(kp_id)


@pytest.mark.asyncio
async def test_create_session_requires_auth(client):
    resp = await client.post(
        "/api/v1/sessions",
        json={"session_type": "practice", "subject": "math"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_session(client, auth_headers, student, db_session):
    from datetime import datetime, timezone
    from app.models.learning import LearningSession

    session = LearningSession(
        student_id=student.id,
        session_type="practice",
        subject="math",
        started_at=datetime.now(timezone.utc),
    )
    db_session.add(session)
    await db_session.flush()

    resp = await client.get(f"/api/v1/sessions/{session.id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(session.id)
    assert data["session_type"] == "practice"


@pytest.mark.asyncio
async def test_get_session_not_found(client, auth_headers):
    resp = await client.get(f"/api/v1/sessions/{uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_session_other_user(client, db_session, student, auth_headers):
    from datetime import datetime, timezone
    from app.core.security import hash_password
    from app.models.learning import LearningSession
    from app.models.user import User

    other_user = User(
        name="other_student",
        role="student",
        password_hash=hash_password("test123"),
    )
    db_session.add(other_user)
    await db_session.flush()

    session = LearningSession(
        student_id=other_user.id,
        session_type="practice",
        subject="math",
        started_at=datetime.now(timezone.utc),
    )
    db_session.add(session)
    await db_session.flush()

    resp = await client.get(f"/api/v1/sessions/{session.id}", headers=auth_headers)
    assert resp.status_code == 404
