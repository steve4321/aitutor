"""Reusable test helper utilities for the AI Tutor test suite."""
from uuid import uuid4

from app.core.security import create_access_token


# ---------------------------------------------------------------------------
# Common test constants
# ---------------------------------------------------------------------------

TEST_USER_ID = str(uuid4())
TEST_PASSWORD = "test123456"
TEST_AUTH_TOKEN = create_access_token({"sub": TEST_USER_ID})


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


def make_auth_headers(user_id: str | None = None) -> dict[str, str]:
    uid = user_id or TEST_USER_ID
    token = create_access_token({"sub": uid})
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Request body helpers
# ---------------------------------------------------------------------------


def make_chat_request(
    content: str = "Hello, tutor!",
    session_id: str | None = None,
) -> dict:
    return {
        "content": content,
        "session_id": session_id,
    }
