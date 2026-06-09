import pytest
from uuid import uuid4

from app.models.course import Course


@pytest.mark.asyncio
async def test_list_courses_empty(client, auth_headers):
    resp = await client.get("/api/v1/courses", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_courses_returns_published(client, published_course, auth_headers):
    resp = await client.get("/api/v1/courses", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["id"] == str(published_course["course_id"])
    assert data[0]["subject"] == "math"


@pytest.mark.asyncio
async def test_list_courses_subject_filter(client, db_session, auth_headers):
    math_course = Course(
        code="MATH-01",
        subject="math",
        name="Math Course",
        is_published=True,
    )
    eng_course = Course(
        code="ENG-01",
        subject="english",
        name="English Course",
        is_published=True,
    )
    db_session.add_all([math_course, eng_course])
    await db_session.flush()

    resp = await client.get("/api/v1/courses?subject=math", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["subject"] == "math"

    resp_all = await client.get("/api/v1/courses?subject=english", headers=auth_headers)
    assert resp_all.status_code == 200
    assert len(resp_all.json()) == 1
    assert resp_all.json()[0]["subject"] == "english"


@pytest.mark.asyncio
async def test_list_courses_requires_auth(client):
    resp = await client.get("/api/v1/courses")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_course_detail(client, published_course, auth_headers):
    course_id = published_course["course_id"]
    resp = await client.get(f"/api/v1/courses/{course_id}", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(course_id)
    assert data["subject"] == "math"
    assert data["name"] == "测试课程"
    assert data["is_published"] is True


@pytest.mark.asyncio
async def test_get_course_detail_not_found(client, auth_headers):
    resp = await client.get(f"/api/v1/courses/{uuid4()}", headers=auth_headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_course_detail_requires_auth(client, published_course):
    resp = await client.get(f"/api/v1/courses/{published_course['course_id']}")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_units(client, published_course, auth_headers):
    course_id = published_course["course_id"]
    resp = await client.get(f"/api/v1/courses/{course_id}/units", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["name"] == "第一章"
    assert data[0]["sort_order"] == 1


@pytest.mark.asyncio
async def test_list_units_empty(client, db_session, auth_headers):
    course = Course(
        code="EMPTY-01",
        subject="math",
        name="No Units",
        is_published=True,
    )
    db_session.add(course)
    await db_session.flush()

    resp = await client.get(f"/api/v1/courses/{course.id}/units", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_lessons(client, published_course, auth_headers):
    course_id = published_course["course_id"]
    resp = await client.get(f"/api/v1/courses/{course_id}/lessons", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "测试课"
    assert data[0]["is_published"] is True


@pytest.mark.asyncio
async def test_list_lessons_empty(client, db_session, auth_headers):
    course = Course(
        code="EMPTY-02",
        subject="math",
        name="No Lessons",
        is_published=True,
    )
    db_session.add(course)
    await db_session.flush()

    resp = await client.get(f"/api/v1/courses/{course.id}/lessons", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json() == []
