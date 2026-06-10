import pytest

from app.core.security import hash_password
from app.models.user import User, ParentLink


@pytest.mark.asyncio
async def test_parent_link_valid_code(client, db_session, student, auth_headers):
    parent = User(
        name="parent_user_1",
        role="parent",
        password_hash=hash_password("test123"),
    )
    db_session.add(parent)
    await db_session.flush()

    parent_code = str(parent.id).replace("-", "")[:6]
    numeric_code = str(int(parent_code, 16) % 1000000).zfill(6)

    resp = await client.post(
        "/api/v1/parent/link",
        json={"link_code": numeric_code},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "linked"
    assert data["parent_name"] == "parent_user_1"


@pytest.mark.asyncio
async def test_parent_link_invalid_code(client, auth_headers):
    resp = await client.post(
        "/api/v1/parent/link",
        json={"link_code": "12345"},
        headers=auth_headers,
    )
    assert resp.status_code == 400

    resp = await client.post(
        "/api/v1/parent/link",
        json={"link_code": "abcdef"},
        headers=auth_headers,
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_parent_link_nonexistent_code(client, db_session, auth_headers):
    resp = await client.post(
        "/api/v1/parent/link",
        json={"link_code": "999999"},
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_parent_link_already_linked(client, db_session, student, auth_headers):
    parent = User(
        name="parent_user_2",
        role="parent",
        password_hash=hash_password("test123"),
    )
    db_session.add(parent)
    await db_session.flush()

    link = ParentLink(
        parent_id=parent.id,
        student_id=student.id,
    )
    db_session.add(link)
    await db_session.flush()

    parent_code = str(parent.id).replace("-", "")[:6]
    numeric_code = str(int(parent_code, 16) % 1000000).zfill(6)

    resp = await client.post(
        "/api/v1/parent/link",
        json={"link_code": numeric_code},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "already_linked"


@pytest.mark.asyncio
async def test_parent_link_requires_auth(client):
    resp = await client.post(
        "/api/v1/parent/link",
        json={"link_code": "123456"},
    )
    assert resp.status_code in (401, 403)
