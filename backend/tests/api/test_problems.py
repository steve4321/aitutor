"""Problems API endpoint tests: GET /api/v1/problems, POST /api/v1/problems/{id}/attempt."""
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_list_problems_works(client, db_session, mcq_problem):
    """GET /problems returns 200 with a list containing seeded problem."""
    await db_session.commit()

    resp = await client.get("/api/v1/problems")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_submit_attempt_requires_auth(client, mcq_problem):
    """POST /problems/{id}/attempt without auth returns 401 or 403."""
    resp = await client.post(
        f"/api/v1/problems/{mcq_problem.id}/attempt",
        json={"answer": "B"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_submit_mcq_correct(client, student, mcq_problem, auth_headers):
    """POST correct MCQ answer with auth returns is_correct=True."""
    mock_agent_result = {
        "agent_response": "Correct! Well done.",
        "structured_data": {"is_correct": True, "evaluation_method": "exact_match"},
        "error": None,
    }
    with patch("app.api.v1.problems.run_agent", new_callable=AsyncMock, return_value=mock_agent_result):
        resp = await client.post(
            f"/api/v1/problems/{mcq_problem.id}/attempt",
            json={"answer": "B"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["is_correct"] is True


@pytest.mark.asyncio
async def test_submit_mcq_wrong(client, student, mcq_problem, auth_headers):
    """POST wrong MCQ answer with auth returns is_correct=False."""
    mock_agent_result = {
        "agent_response": "Not quite. The correct answer is B.",
        "structured_data": {"is_correct": False, "evaluation_method": "exact_match"},
        "error": None,
    }
    with patch("app.api.v1.problems.run_agent", new_callable=AsyncMock, return_value=mock_agent_result):
        resp = await client.post(
            f"/api/v1/problems/{mcq_problem.id}/attempt",
            json={"answer": "A"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.json()["is_correct"] is False


@pytest.mark.asyncio
async def test_submit_returns_error_type_field(client, student, mcq_problem, auth_headers):
    """AttemptResponse always includes error_type (even if null)."""
    mock_agent_result = {
        "agent_response": "Correct!",
        "structured_data": {"is_correct": True, "error_type": None},
        "error": None,
    }
    with patch("app.api.v1.problems.run_agent", new_callable=AsyncMock, return_value=mock_agent_result):
        resp = await client.post(
            f"/api/v1/problems/{mcq_problem.id}/attempt",
            json={"answer": "B"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "error_type" in data
