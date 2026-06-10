import pytest
from sqlalchemy import select

from app.models.user import User, StudentProfile


@pytest.fixture(autouse=True)
def _reset_rate_limit():
    from app.core.rate_limit import limiter
    limiter.reset()
    yield
    limiter.reset()


@pytest.mark.asyncio
async def test_login_success(client, student):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "测试小明", "password": "test123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, student):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "测试小明", "password": "wrongpassword"},
    )
    assert resp.status_code == 401
    assert "Invalid username or password" in resp.json()["error"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client, db_session):
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": "ghost", "password": "test123"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_missing_fields(client, db_session):
    resp = await client.post("/api/v1/auth/login", json={"username": "foo"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_register_success(client, db_session):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"username": "newuser", "password": "abc123"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data

    result = await db_session.execute(select(User).where(User.name == "newuser"))
    user = result.scalar_one()
    assert user.role == "student"

    result = await db_session.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    assert profile is not None


@pytest.mark.asyncio
async def test_register_duplicate_username(client, student):
    resp = await client.post(
        "/api/v1/auth/register",
        json={"username": "测试小明", "password": "abc123"},
    )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_creates_student_role(client, db_session):
    await client.post(
        "/api/v1/auth/register",
        json={"username": "rolecheck", "password": "abc123"},
    )
    result = await db_session.execute(select(User).where(User.name == "rolecheck"))
    user = result.scalar_one()
    assert user.role == "student"


@pytest.mark.asyncio
async def test_register_creates_student_profile(client, db_session):
    await client.post(
        "/api/v1/auth/register",
        json={"username": "profilecheck", "password": "abc123"},
    )
    result = await db_session.execute(select(User).where(User.name == "profilecheck"))
    user = result.scalar_one()
    result = await db_session.execute(
        select(StudentProfile).where(StudentProfile.user_id == user.id)
    )
    profile = result.scalar_one_or_none()
    assert profile is not None
    assert profile.preferred_lang == "zh-CN"


@pytest.mark.asyncio
async def test_register_missing_fields(client, db_session):
    resp = await client.post("/api/v1/auth/register", json={"username": "foo"})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_refresh_valid_token(client, student):
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "测试小明", "password": "test123"},
    )
    refresh_token = login.json()["refresh_token"]

    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_refresh_invalid_token(client, db_session):
    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "invalid.token.here"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_uses_access_token_rejected(client, student):
    login = await client.post(
        "/api/v1/auth/login",
        json={"username": "测试小明", "password": "test123"},
    )
    access_token = login.json()["access_token"]

    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": access_token},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_refresh_deleted_user(client, student, db_session):
    from app.core.security import create_refresh_token

    token = create_refresh_token({"sub": str(student.id)})
    await db_session.delete(student)
    await db_session.flush()

    resp = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": token},
    )
    assert resp.status_code == 401
