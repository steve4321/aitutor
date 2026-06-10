import pytest

from app.models.user import User


@pytest.mark.asyncio
async def test_get_me_authenticated(client, student, auth_headers):
    resp = await client.get("/api/v1/users/me", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "测试小明"
    assert data["role"] == "student"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_me_unauthenticated(client, db_session):
    resp = await client.get("/api/v1/users/me")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_update_me_name(client, student, auth_headers, db_session):
    resp = await client.put(
        "/api/v1/users/me",
        json={"name": "新名字"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "新名字"


@pytest.mark.asyncio
async def test_update_me_unauthenticated(client, db_session):
    resp = await client.put(
        "/api/v1/users/me",
        json={"name": "新名字"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_profile_with_existing_profile(client, student, auth_headers):
    resp = await client.get("/api/v1/users/me/profile", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["grade_level"] == 5
    assert data["target_exam"] == "AMC8"
    assert data["preferred_lang"] == "zh-CN"


@pytest.mark.asyncio
async def test_get_profile_not_found(client, db_session):
    from app.core.security import hash_password, create_access_token

    user = User(
        name="noprobfile",
        role="student",
        password_hash=hash_password("test123a"),
    )
    db_session.add(user)
    await db_session.flush()
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.get("/api/v1/users/me/profile", headers=headers)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_patch_profile_grade_level(client, student, auth_headers):
    resp = await client.patch(
        "/api/v1/users/me/profile",
        json={"grade_level": 8},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["grade_level"] == 8


@pytest.mark.asyncio
async def test_patch_profile_target_exam(client, student, auth_headers):
    resp = await client.patch(
        "/api/v1/users/me/profile",
        json={"target_exam": "AMC10"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["target_exam"] == "AMC10"


@pytest.mark.asyncio
async def test_patch_profile_both_fields(client, student, auth_headers):
    resp = await client.patch(
        "/api/v1/users/me/profile",
        json={"grade_level": 10, "target_exam": "AMC12"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["grade_level"] == 10
    assert data["target_exam"] == "AMC12"


@pytest.mark.asyncio
async def test_patch_profile_not_found(client, db_session):
    from app.core.security import hash_password, create_access_token

    user = User(
        name="noprobfile2",
        role="student",
        password_hash=hash_password("test123a"),
    )
    db_session.add(user)
    await db_session.flush()
    token = create_access_token({"sub": str(user.id)})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.patch(
        "/api/v1/users/me/profile",
        json={"grade_level": 7},
        headers=headers,
    )
    assert resp.status_code == 404
