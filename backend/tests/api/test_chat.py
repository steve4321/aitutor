"""Chat API endpoint tests: POST /api/v1/chat/message."""
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4


@pytest.mark.asyncio
async def test_send_message_requires_auth(client):
    """POST /chat/message without Authorization header returns 401 or 403."""
    resp = await client.post(
        "/api/v1/chat/message",
        json={"content": "你好"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_send_message_creates_session(client, student, auth_headers):
    """POST without session_id auto-creates a new session."""
    mock_result = {
        "agent_response": "Hello! How can I help?",
        "structured_data": None,
        "error": None,
    }
    with patch("app.api.v1.chat.run_agent", new_callable=AsyncMock, return_value=mock_result):
        resp = await client.post(
            "/api/v1/chat/message",
            json={"content": "你好"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["role"] == "assistant"
    assert data["session_id"] is not None


@pytest.mark.asyncio
async def test_send_message_existing_session(client, student, db_session, auth_headers):
    """POST with an existing session_id reuses that session."""
    from app.models.learning import LearningSession

    session = LearningSession(
        student_id=student.id,
        session_type="chat",
        subject="general",
        started_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    db_session.add(session)
    await db_session.commit()

    mock_result = {
        "agent_response": "Continuing our chat!",
        "structured_data": None,
        "error": None,
    }
    with patch("app.api.v1.chat.run_agent", new_callable=AsyncMock, return_value=mock_result):
        resp = await client.post(
            "/api/v1/chat/message",
            json={"content": "继续聊", "session_id": str(session.id)},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["session_id"] == str(session.id)


@pytest.mark.asyncio
async def test_send_message_invalid_session_404(client, student, auth_headers):
    """POST with a non-existent session_id returns 404."""
    fake_id = str(uuid4())
    mock_result = {
        "agent_response": "x",
        "structured_data": None,
        "error": None,
    }
    with patch("app.api.v1.chat.run_agent", new_callable=AsyncMock, return_value=mock_result):
        resp = await client.post(
            "/api/v1/chat/message",
            json={"content": "hi", "session_id": fake_id},
            headers=auth_headers,
        )

    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_send_message_returns_session_id(client, student, auth_headers):
    """Every successful response includes a session_id field."""
    mock_result = {
        "agent_response": "Got it!",
        "structured_data": None,
        "error": None,
    }
    with patch("app.api.v1.chat.run_agent", new_callable=AsyncMock, return_value=mock_result):
        resp = await client.post(
            "/api/v1/chat/message",
            json={"content": "test"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert data["session_id"] is not None
