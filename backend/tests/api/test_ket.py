import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage

from app.models.ket import KETQuestion, KETWritingTask, KETSpeakingTask


@pytest.mark.asyncio
async def test_list_questions_returns_empty(client, auth_headers):
    resp = await client.get("/api/v1/ket/questions", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_questions_with_skill_filter(client, auth_headers, db_session):
    q1 = KETQuestion(
        skill="reading",
        level="A2",
        question_type="mcq",
        prompt="Read the text and answer.",
        correct_answer="A",
        options={"A": "Yes", "B": "No"},
    )
    q2 = KETQuestion(
        skill="listening",
        level="A2",
        question_type="mcq",
        prompt="Listen and answer.",
        correct_answer="B",
        options={"A": "Yes", "B": "No"},
    )
    db_session.add_all([q1, q2])
    await db_session.flush()

    resp = await client.get("/api/v1/ket/questions?skill=reading", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 1
    assert data["items"][0]["skill"] == "reading"


@pytest.mark.asyncio
async def test_get_question_returns_404(client, auth_headers):
    resp = await client.get(
        "/api/v1/ket/questions/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_writing_tasks_returns_tasks(client, auth_headers, db_session):
    task = KETWritingTask(
        task_type="email",
        prompt="Write an email to your friend about your weekend.",
    )
    db_session.add(task)
    await db_session.flush()

    resp = await client.get("/api/v1/ket/writing/tasks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["task_type"] == "email"


@pytest.mark.asyncio
async def test_list_writing_tasks_filters_by_type(client, auth_headers, db_session):
    t1 = KETWritingTask(task_type="email", prompt="Write an email.")
    t2 = KETWritingTask(task_type="story", prompt="Write a story.")
    db_session.add_all([t1, t2])
    await db_session.flush()

    resp = await client.get("/api/v1/ket/writing/tasks?task_type=email", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["task_type"] == "email"


@pytest.mark.asyncio
async def test_submit_writing_requires_auth(client):
    resp = await client.post(
        "/api/v1/ket/writing/submit",
        json={"task_id": "00000000-0000-0000-0000-000000000000", "content": "Hello", "word_count": 1},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_submit_writing_validates_word_count(client, auth_headers, db_session):
    task = KETWritingTask(
        task_type="email",
        prompt="Write an email.",
        word_limit_min=25,
        word_limit_max=50,
    )
    db_session.add(task)
    await db_session.flush()

    resp = await client.post(
        "/api/v1/ket/writing/submit",
        json={"task_id": str(task.id), "content": "Hi", "word_count": 2},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 0
    assert "below the minimum" in data["feedback"]


@pytest.mark.asyncio
async def test_submit_writing_with_llm_mocked(client, auth_headers, db_session):
    task = KETWritingTask(
        task_type="email",
        prompt="Write an email to your friend.",
        word_limit_min=10,
        word_limit_max=50,
    )
    db_session.add(task)
    await db_session.flush()

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=AIMessage(
            content='{"score": 85, "content_score": 80, "organization_score": 90, '
            '"language_score": 85, "feedback": "Good work!", "band": 4.5}'
        )
    )

    with patch("app.services.ket_service.get_llm", return_value=mock_llm), \
         patch("app.services.ket_service.is_llm_available", return_value=True):
        resp = await client.post(
            "/api/v1/ket/writing/submit",
            json={
                "task_id": str(task.id),
                "content": "Dear friend, I had a great weekend. I went to the park and played football.",
                "word_count": 16,
            },
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 85
    assert data["band"] == 4.5


@pytest.mark.asyncio
async def test_submit_writing_returns_404_for_missing_task(client, auth_headers):
    resp = await client.post(
        "/api/v1/ket/writing/submit",
        json={
            "task_id": "00000000-0000-0000-0000-000000000000",
            "content": "Hello world",
            "word_count": 2,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_speaking_tasks_returns_tasks(client, auth_headers, db_session):
    task = KETSpeakingTask(
        topic="Hobbies",
        question="What do you like to do in your free time?",
        difficulty="easy",
    )
    db_session.add(task)
    await db_session.flush()

    resp = await client.get("/api/v1/ket/speaking/tasks", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["topic"] == "Hobbies"


@pytest.mark.asyncio
async def test_list_speaking_tasks_filters_by_difficulty(client, auth_headers, db_session):
    t1 = KETSpeakingTask(topic="Hobbies", question="Q1", difficulty="easy")
    t2 = KETSpeakingTask(topic="Food", question="Q2", difficulty="hard")
    db_session.add_all([t1, t2])
    await db_session.flush()

    resp = await client.get("/api/v1/ket/speaking/tasks?difficulty=easy", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["difficulty"] == "easy"


@pytest.mark.asyncio
async def test_submit_speaking_requires_auth(client):
    resp = await client.post(
        "/api/v1/ket/speaking/submit",
        json={
            "task_id": "00000000-0000-0000-0000-000000000000",
            "transcript": "Hello",
            "audio_duration_sec": 10,
        },
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_submit_speaking_returns_404_for_missing_task(client, auth_headers):
    resp = await client.post(
        "/api/v1/ket/speaking/submit",
        json={
            "task_id": "00000000-0000-0000-0000-000000000000",
            "transcript": "Hello",
            "audio_duration_sec": 10,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_questions_endpoint_requires_auth(client):
    resp = await client.get("/api/v1/ket/questions")
    assert resp.status_code in (401, 403)
