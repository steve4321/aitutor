"""Tests for memory service and profile service."""
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from langchain_core.messages import AIMessage

from app.agents.services.memory import (
    format_summaries_for_prompt,
    summary_to_dict,
    build_student_memory_context,
    build_prerequisite_context,
)
from app.agents.services.profile_service import update_student_profile_from_summary
from app.models.memory import SessionSummary


# ── format_summaries_for_prompt ──────────────────────────────────────────


def test_format_summaries_empty():
    result = format_summaries_for_prompt([])
    assert "暂无" in result


def test_format_summaries_with_data():
    s = MagicMock(spec=SessionSummary)
    s.generated_at = datetime(2026, 6, 15, 10, 30)
    s.summary_text = "复习了勾股定理"
    s.topics_discussed = ["勾股定理", "面积计算"]
    s.sentiment = "positive"
    s.pending_items = ["练习圆的定理"]

    result = format_summaries_for_prompt([s])
    assert "复习了勾股定理" in result
    assert "勾股定理" in result
    assert "positive" in result
    assert "圆的定理" in result


# ── summary_to_dict ──────────────────────────────────────────────────────


def test_summary_to_dict_basic():
    s = MagicMock(spec=SessionSummary)
    s.id = uuid4()
    s.session_id = uuid4()
    s.summary_text = "summary"
    s.topics_discussed = ["t1"]
    s.knowledge_points_touched = ["k1"]
    s.sentiment = "neutral"
    s.pending_items = []
    s.generated_at = datetime(2026, 6, 15, 12, 0)

    d = summary_to_dict(s)
    assert d["summary_text"] == "summary"
    assert d["sentiment"] == "neutral"
    assert d["topics_discussed"] == ["t1"]


# ── update_student_profile_from_summary ────────────────────────────────


@pytest.mark.asyncio
async def test_update_profile_increments_session_count():
    student_id = uuid4()
    profile = MagicMock()
    profile.session_count_total = 0
    profile.interaction_pattern = None
    profile.emotional_trend = None
    profile.learning_style = None

    summary = MagicMock(spec=SessionSummary)
    summary.interaction_style = {"hint_level_avg": 1.5, "response_detail": "verbose"}
    summary.sentiment = "positive"
    summary.pending_items = ["复习圆的定理"]

    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=profile)))

    await update_student_profile_from_summary(db, student_id, summary)
    assert profile.session_count_total == 1
    assert profile.interaction_pattern["response_detail"] == "verbose"
    assert profile.interaction_pattern["hint_level_avg"] == 1.5
    assert profile.emotional_trend["recent_sentiments"] == ["positive"]
    assert "复习圆的定理" in profile.interaction_pattern["pending_items"]


@pytest.mark.asyncio
async def test_update_profile_no_profile_returns_silently():
    student_id = uuid4()
    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=None)))
    summary = MagicMock(spec=SessionSummary)
    summary.interaction_style = None
    summary.sentiment = None
    summary.pending_items = None
    await update_student_profile_from_summary(db, student_id, summary)


@pytest.mark.asyncio
async def test_update_profile_learns_style_after_3_sessions():
    student_id = uuid4()
    profile = MagicMock()
    profile.session_count_total = 2
    profile.interaction_pattern = {"response_detail": "verbose"}
    profile.emotional_trend = None
    profile.learning_style = None

    summary = MagicMock(spec=SessionSummary)
    summary.interaction_style = {"response_detail": "verbose"}
    summary.sentiment = None
    summary.pending_items = None

    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=profile)))
    await update_student_profile_from_summary(db, student_id, summary)
    assert profile.learning_style == "reading"


# ── build_student_memory_context ────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_memory_context_no_summaries():
    profile = MagicMock()
    profile.learning_style = "visual"
    profile.pace_category = None
    profile.interaction_pattern = {"hint_level_avg": 1.0}
    profile.emotional_trend = {"recent_sentiments": ["positive"]}

    db = AsyncMock()
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
    db.execute.return_value.scalars.return_value.all.return_value = []
    db.execute2 = AsyncMock(return_value=MagicMock(scalar_one_or_none=MagicMock(return_value=profile)))

    call_count = [0]

    async def execute_side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[]))))
        return MagicMock(scalar_one_or_none=MagicMock(return_value=profile))

    db.execute = AsyncMock(side_effect=execute_side_effect)
    result = await build_student_memory_context(db, uuid4())
    assert "学习风格" in result or "暂无" in result


# ── build_prerequisite_context ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_build_prerequisite_no_kp_id():
    db = AsyncMock()
    result = await build_prerequisite_context(db, uuid4(), current_kp_id=None)
    assert result == ""


@pytest.mark.asyncio
async def test_build_prerequisite_no_deps():
    kp = MagicMock()
    kp.id = uuid4()
    kp.name = "勾股定理"
    kp.pillar = "geometry"

    db = AsyncMock()
    db.get = AsyncMock(return_value=kp)
    db.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))

    result = await build_prerequisite_context(db, uuid4(), current_kp_id=kp.id)
    assert result == ""
