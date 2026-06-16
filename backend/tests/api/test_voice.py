"""Voice API endpoint tests: TTS, ASR, pronunciation scoring, voices, parse-math."""
from unittest.mock import AsyncMock, patch

import pytest


@pytest.mark.asyncio
async def test_tts_success(client, auth_headers):
    """POST /voice/tts returns audio bytes when TTS service succeeds."""
    fake_audio = b"\x49\x44\x33\x03\x00\x00\x00"
    with patch(
        "app.api.v1.voice.tts_service.text_to_speech",
        new_callable=AsyncMock,
        return_value=fake_audio,
    ):
        resp = await client.post(
            "/api/v1/voice/tts",
            json={"text": "你好世界", "voice": "zh-CN-XiaoxiaoNeural", "rate": "+0%"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/mpeg"
    assert resp.content == fake_audio


@pytest.mark.asyncio
async def test_tts_service_unavailable(client, auth_headers):
    """POST /voice/tts returns 503 when TTS service returns None."""
    with patch(
        "app.api.v1.voice.tts_service.text_to_speech",
        new_callable=AsyncMock,
        return_value=None,
    ):
        resp = await client.post(
            "/api/v1/voice/tts",
            json={"text": "你好"},
            headers=auth_headers,
        )

    assert resp.status_code == 503
    assert resp.json()["error"] == "TTS service unavailable"


@pytest.mark.asyncio
async def test_tts_requires_auth(client):
    """POST /voice/tts without auth returns 401 or 403."""
    resp = await client.post(
        "/api/v1/voice/tts",
        json={"text": "你好"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_asr_success(client, auth_headers):
    """POST /voice/asr returns transcript when ASR service succeeds."""
    mock_result = {
        "transcript": "二加二等于四",
        "language": "zh",
        "confidence": 0.95,
    }
    with patch(
        "app.api.v1.voice.asr_service.transcribe_audio",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/voice/asr",
            files={"audio": ("test.webm", b"fake-audio-data", "audio/webm")},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["transcript"] == "二加二等于四"
    assert data["language"] == "zh"
    assert data["confidence"] == 0.95


@pytest.mark.asyncio
async def test_asr_empty_audio(client, auth_headers):
    """POST /voice/asr returns 400 for an empty audio upload."""
    resp = await client.post(
        "/api/v1/voice/asr",
        files={"audio": ("empty.webm", b"", "audio/webm")},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "Empty audio file"


@pytest.mark.asyncio
async def test_asr_service_error(client, auth_headers):
    """POST /voice/asr returns 503 when ASR returns an error."""
    error_result = {
        "transcript": "",
        "language": "zh",
        "confidence": 0.0,
        "error": "ASR unavailable",
    }
    with patch(
        "app.api.v1.voice.asr_service.transcribe_audio",
        new_callable=AsyncMock,
        return_value=error_result,
    ):
        resp = await client.post(
            "/api/v1/voice/asr",
            files={"audio": ("test.webm", b"fake-audio", "audio/webm")},
            headers=auth_headers,
        )

    assert resp.status_code == 503
    assert resp.json()["error"] == "ASR unavailable"


@pytest.mark.asyncio
async def test_asr_requires_auth(client):
    """POST /voice/asr without auth returns 401 or 403."""
    resp = await client.post(
        "/api/v1/voice/asr",
        files={"audio": ("test.webm", b"data", "audio/webm")},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_score_pronunciation_success(client, auth_headers):
    """POST /voice/score-pronunciation returns score when ASR succeeds."""
    mock_result = {
        "score": 85,
        "confidence": 0.9,
        "transcript": "hello world",
        "word_scores": [{"word": "hello", "score": 100, "heard": "hello"}],
    }
    with patch(
        "app.api.v1.voice.asr_service.score_pronunciation",
        new_callable=AsyncMock,
        return_value=mock_result,
    ):
        resp = await client.post(
            "/api/v1/voice/score-pronunciation",
            files={"audio": ("test.webm", b"fake-audio", "audio/webm")},
            params={"reference_text": "hello world", "language": "en"},
            headers=auth_headers,
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["score"] == 85
    assert data["confidence"] == 0.9
    assert data["transcript"] == "hello world"


@pytest.mark.asyncio
async def test_score_pronunciation_empty_audio(client, auth_headers):
    """POST /voice/score-pronunciation returns 400 for empty audio."""
    resp = await client.post(
        "/api/v1/voice/score-pronunciation",
        files={"audio": ("empty.webm", b"", "audio/webm")},
        params={"reference_text": "hello"},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "Empty audio file"


@pytest.mark.asyncio
async def test_score_pronunciation_service_error(client, auth_headers):
    """POST /voice/score-pronunciation returns 503 when ASR returns an error."""
    error_result = {
        "score": 0,
        "confidence": 0.0,
        "transcript": "",
        "error": "Could not transcribe audio",
    }
    with patch(
        "app.api.v1.voice.asr_service.score_pronunciation",
        new_callable=AsyncMock,
        return_value=error_result,
    ):
        resp = await client.post(
            "/api/v1/voice/score-pronunciation",
            files={"audio": ("test.webm", b"fake-audio", "audio/webm")},
            params={"reference_text": "hello world", "language": "en"},
            headers=auth_headers,
        )

    assert resp.status_code == 503
    assert resp.json()["error"] == "Could not transcribe audio"


@pytest.mark.asyncio
async def test_score_pronunciation_requires_auth(client):
    """POST /voice/score-pronunciation without auth returns 401 or 403."""
    resp = await client.post(
        "/api/v1/voice/score-pronunciation",
        files={"audio": ("test.webm", b"data", "audio/webm")},
        params={"reference_text": "hello"},
    )
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_list_voices(client, auth_headers):
    """GET /voice/voices returns the list of supported voices."""
    resp = await client.get("/api/v1/voice/voices", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    voice_ids = {v["id"] for v in data}
    assert "zh-CN-XiaoxiaoNeural" in voice_ids
    for voice in data:
        assert "id" in voice
        assert "lang" in voice
        assert "gender" in voice
        assert "label" in voice


@pytest.mark.asyncio
async def test_list_voices_requires_auth(client):
    """GET /voice/voices without auth returns 401 or 403."""
    resp = await client.get("/api/v1/voice/voices")
    assert resp.status_code in (401, 403)


@pytest.mark.asyncio
async def test_parse_math(client, auth_headers):
    """POST /voice/parse-math converts spoken Chinese math to symbolic form."""
    resp = await client.post(
        "/api/v1/voice/parse-math",
        json={"text": "x平方加5x加6"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["parsed"] == "x^2+5x+6"


@pytest.mark.asyncio
async def test_parse_math_missing_text(client, auth_headers):
    """POST /voice/parse-math returns 400 when 'text' field is missing."""
    resp = await client.post(
        "/api/v1/voice/parse-math",
        json={},
        headers=auth_headers,
    )
    assert resp.status_code == 400
    assert resp.json()["error"] == "Missing 'text' field"


@pytest.mark.asyncio
async def test_parse_math_requires_auth(client):
    """POST /voice/parse-math without auth returns 401 or 403."""
    resp = await client.post(
        "/api/v1/voice/parse-math",
        json={"text": "x平方"},
    )
    assert resp.status_code in (401, 403)
