import pytest

from app.core.security import verify_password
from app.services.auth_service import authenticate_user, register_user


@pytest.mark.asyncio
async def test_register_user_creates_user_with_hashed_password(db_session):
    user = await register_user(db_session, email="a@b.com", phone=None, name="alice", password="secret123")
    assert user.name == "alice"
    assert user.email == "a@b.com"
    assert user.phone is None
    assert user.password_hash != "secret123"
    assert verify_password("secret123", user.password_hash)
    assert user.role == "student"


@pytest.mark.asyncio
async def test_register_user_default_role_is_student(db_session):
    user = await register_user(db_session, email=None, phone=None, name="bob", password="pw")
    assert user.role == "student"


@pytest.mark.asyncio
async def test_register_user_accepts_custom_role(db_session):
    user = await register_user(db_session, email=None, phone=None, name="admin1", password="pw", role="admin")
    assert user.role == "admin"


@pytest.mark.asyncio
async def test_register_user_duplicate_name_raises(db_session):
    await register_user(db_session, email=None, phone=None, name="dup", password="pw")
    with pytest.raises(ValueError, match="already exists"):
        await register_user(db_session, email="other@b.com", phone=None, name="dup", password="pw2")


@pytest.mark.asyncio
async def test_register_user_optional_email_and_phone(db_session):
    user = await register_user(db_session, email=None, phone=None, name="nocontact", password="pw")
    assert user.email is None
    assert user.phone is None

    user2 = await register_user(db_session, email="x@y.com", phone="1234567890", name="withcontact", password="pw")
    assert user2.email == "x@y.com"
    assert user2.phone == "1234567890"


@pytest.mark.asyncio
async def test_register_user_password_is_hashed_not_plaintext(db_session):
    user = await register_user(db_session, email=None, phone=None, name="hashcheck", password="mypassword")
    assert "$" in user.password_hash
    assert user.password_hash != "mypassword"
    parts = user.password_hash.split("$")
    assert len(parts) == 2


@pytest.mark.asyncio
async def test_authenticate_user_correct_credentials(db_session):
    await register_user(db_session, email=None, phone=None, name="logintest", password="pass123")
    user = await authenticate_user(db_session, login="logintest", password="pass123")
    assert user is not None
    assert user.name == "logintest"


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password(db_session):
    await register_user(db_session, email=None, phone=None, name="wrongpw", password="correct")
    user = await authenticate_user(db_session, login="wrongpw", password="incorrect")
    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user_nonexistent_user(db_session):
    user = await authenticate_user(db_session, login="ghost", password="anything")
    assert user is None
