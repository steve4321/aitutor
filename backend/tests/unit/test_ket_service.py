import pytest
from unittest.mock import AsyncMock, patch
from langchain_core.messages import AIMessage

from app.models.ket import KETWritingTask, KETSpeakingTask
from app.services.ket_service import score_writing, score_speaking, _writing_fallback, _speaking_fallback


@pytest.mark.asyncio
async def test_score_writing_returns_valid_dict(db_session):
    task = KETWritingTask(
        task_type="email",
        prompt="Write an email.",
        word_limit_min=5,
        word_limit_max=50,
    )
    db_session.add(task)
    await db_session.flush()

    result = await score_writing(
        db_session, task,
        "Dear friend, I had a great weekend with my family. We went to the park.",
        14,
    )
    assert "score" in result
    assert "content_score" in result
    assert "organization_score" in result
    assert "language_score" in result
    assert "feedback" in result
    assert "band" in result
    assert 0 <= result["band"] <= 5.0


@pytest.mark.asyncio
async def test_score_writing_fallback_when_llm_unavailable(db_session):
    task = KETWritingTask(
        task_type="story",
        prompt="Write a short story.",
        word_limit_min=5,
        word_limit_max=50,
    )
    db_session.add(task)
    await db_session.flush()

    with patch("app.services.ket_service.is_llm_available", return_value=False):
        result = await score_writing(
            db_session, task,
            "Once upon a time there was a small cat who lived in a big house by the river.",
            17,
        )
    assert result["score"] > 0
    assert result["band"] > 0


@pytest.mark.asyncio
async def test_score_writing_llm_returns_parsed_score(db_session):
    task = KETWritingTask(
        task_type="email",
        prompt="Write an email.",
        word_limit_min=5,
        word_limit_max=50,
    )
    db_session.add(task)
    await db_session.flush()

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=AIMessage(
            content='{"score": 75, "content_score": 70, "organization_score": 80, '
            '"language_score": 75, "feedback": "Well done!", "band": 4.0}'
        )
    )

    with patch("app.services.ket_service.get_llm", return_value=mock_llm), \
         patch("app.services.ket_service.is_llm_available", return_value=True):
        result = await score_writing(
            db_session, task,
            "Dear friend, I had a wonderful weekend. Thank you for asking.",
            12,
        )
    assert result["score"] == 75
    assert result["band"] == 4.0
    assert result["feedback"] == "Well done!"


@pytest.mark.asyncio
async def test_score_writing_below_min_words(db_session):
    task = KETWritingTask(
        task_type="email",
        prompt="Write an email.",
        word_limit_min=25,
        word_limit_max=50,
    )
    db_session.add(task)
    await db_session.flush()

    result = await score_writing(db_session, task, "Hi there", 2)
    assert result["score"] == 0
    assert result["band"] == 0
    assert "below the minimum" in result["feedback"]


@pytest.mark.asyncio
async def test_score_speaking_handles_empty_transcript(db_session):
    task = KETSpeakingTask(
        topic="Hobbies",
        question="What do you like?",
        difficulty="easy",
        expected_duration_sec=30,
    )
    db_session.add(task)
    await db_session.flush()

    result = await score_speaking(db_session, task, "", 10)
    assert result["score"] == 0
    assert result["band"] == 0
    assert "No transcript" in result["feedback"]


@pytest.mark.asyncio
async def test_score_speaking_fallback(db_session):
    task = KETSpeakingTask(
        topic="Daily routine",
        question="Tell me about your day.",
        difficulty="easy",
        expected_duration_sec=30,
    )
    db_session.add(task)
    await db_session.flush()

    with patch("app.services.ket_service.is_llm_available", return_value=False):
        result = await score_speaking(
            db_session, task,
            "I wake up at seven oclock and I have breakfast then I go to school",
            25,
        )
    assert result["score"] > 0
    assert result["band"] > 0
    assert "feedback" in result


@pytest.mark.asyncio
async def test_score_speaking_llm_returns_parsed_score(db_session):
    task = KETSpeakingTask(
        topic="Hobbies",
        question="What are your hobbies?",
        difficulty="easy",
        expected_duration_sec=30,
    )
    db_session.add(task)
    await db_session.flush()

    mock_llm = AsyncMock()
    mock_llm.ainvoke = AsyncMock(
        return_value=AIMessage(
            content='{"score": 80, "band": 4.0, "feedback": "Great answer!"}'
        )
    )

    with patch("app.services.ket_service.get_llm", return_value=mock_llm), \
         patch("app.services.ket_service.is_llm_available", return_value=True):
        result = await score_speaking(
            db_session, task,
            "I like playing football and reading books in my free time.",
            20,
        )
    assert result["score"] == 80
    assert result["band"] == 4.0


@pytest.mark.asyncio
async def test_writing_fallback_scores_are_bounded():
    result = _writing_fallback("Hello world. This is a test sentence for the fallback.", 10, 5, 50)
    assert 0 <= result["score"] <= 100
    assert 0 <= result["band"] <= 5.0


@pytest.mark.asyncio
async def test_speaking_fallback_scores_are_bounded():
    result = _speaking_fallback("I like to play football and read books.", 15, 30)
    assert 0 <= result["score"] <= 100
    assert 0 <= result["band"] <= 5.0
