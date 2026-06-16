"""Animation API endpoint tests: POST /render, GET /{id}."""
import json
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from app.schemas.animation import AnimationResult


def _minimal_timeline() -> dict:
    return {
        "title": "Test Animation",
        "width": 1280,
        "height": 720,
        "fps": 30,
        "background_color": "#1a1a2e",
        "elements": [
            {
                "id": "text1",
                "type": "text_label",
                "config": {
                    "text": "Hello",
                    "font_size": 36,
                    "color": "#FFFFFF",
                    "position": [0, 0, 0],
                },
                "layer": 0,
            }
        ],
        "steps": [
            {
                "time_start": 0,
                "duration": 1.0,
                "action": "write",
                "target_element_id": "text1",
                "params": {},
            }
        ],
        "narration": "",
        "voice": "zh-CN-YunxiNeural",
    }


@pytest.mark.asyncio
async def test_render_animation_success(client, auth_headers, tmp_path):
    """POST /animations/render returns 200 when pipeline succeeds."""
    fake_result = AnimationResult(status="static", static_steps=["Step 1"])

    with patch(
        "app.api.v1.animations.render_animation_pipeline",
        new_callable=AsyncMock,
        return_value=fake_result,
    ), patch(
        "app.api.v1.animations.ANIMATION_OUTPUT_DIR",
        tmp_path,
    ):
        resp = await client.post(
            "/api/v1/animations/render",
            json=_minimal_timeline(),
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["result"]["status"] == "static"
    assert data["result"]["static_steps"] == ["Step 1"]


@pytest.mark.asyncio
async def test_render_animation_failure(client, auth_headers, tmp_path):
    """POST /animations/render returns 500 when pipeline raises."""
    with patch(
        "app.api.v1.animations.render_animation_pipeline",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Manim not found"),
    ), patch(
        "app.api.v1.animations.ANIMATION_OUTPUT_DIR",
        tmp_path,
    ):
        resp = await client.post(
            "/api/v1/animations/render",
            json=_minimal_timeline(),
            headers=auth_headers,
        )

    assert resp.status_code == 500
    assert "Manim not found" in resp.json()["error"]


@pytest.mark.asyncio
async def test_render_animation_requires_auth(client):
    """POST /animations/render without auth returns 401 or 403."""
    resp = await client.post(
        "/api/v1/animations/render",
        json=_minimal_timeline(),
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_get_animation_not_found(client, auth_headers, tmp_path):
    """GET /animations/{id} returns 404 for a non-existent animation."""
    with patch("app.api.v1.animations.ANIMATION_OUTPUT_DIR", tmp_path):
        resp = await client.get(
            f"/api/v1/animations/{uuid4()}",
            headers=auth_headers,
        )
    assert resp.status_code == 404
    assert resp.json()["error"] == "Animation not found"


@pytest.mark.asyncio
async def test_get_animation_success(client, auth_headers, tmp_path):
    """GET /animations/{id} returns 200 with the stored result."""
    animation_id = uuid4()
    result_dir = tmp_path / str(animation_id)
    result_dir.mkdir(parents=True)
    stored_result = AnimationResult(
        status="video",
        video_path="/data/out.mp4",
        duration_sec=5.0,
    )
    (result_dir / "result.json").write_text(
        json.dumps(
            {"id": str(animation_id), "result": stored_result.model_dump(mode="json")},
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    with patch("app.api.v1.animations.ANIMATION_OUTPUT_DIR", tmp_path):
        resp = await client.get(
            f"/api/v1/animations/{animation_id}",
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == str(animation_id)
    assert data["result"]["status"] == "video"
    assert data["result"]["video_path"] == "/data/out.mp4"


@pytest.mark.asyncio
async def test_get_animation_requires_auth(client):
    """GET /animations/{id} without auth returns 401 or 403."""
    resp = await client.get(f"/api/v1/animations/{uuid4()}")
    assert resp.status_code in (401, 403)
