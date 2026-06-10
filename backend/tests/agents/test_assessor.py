"""Tests for assessor_agent — answer evaluation, prompt selection, knowledge updates."""
from unittest.mock import patch
from uuid import uuid4

import pytest

from app.agents.assessor_agent import (
    _select_assessment_prompt,
    assessor_node,
)


def _make_state(**overrides) -> dict:
    base = {
        "session_id": str(uuid4()),
        "student_id": str(uuid4()),
        "user_message": "",
        "request_type": "attempt",
        "student_answer": "B",
        "problem_data": {
            "format": "mcq",
            "correct_answer": "B",
            "knowledge_point_ids": [str(uuid4())],
        },
        "hint_level": 0,
    }
    base.update(overrides)
    return base


# ── MCQ tests (no LLM needed) ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mcq_correct():
    result = await assessor_node(_make_state(student_answer="B", problem_data={
        "format": "mcq", "correct_answer": "B",
        "knowledge_point_ids": [str(uuid4())],
    }))

    assert result["structured_data"]["is_correct"] is True
    assert "Correct" in result["agent_response"]


@pytest.mark.asyncio
async def test_mcq_wrong():
    result = await assessor_node(_make_state(student_answer="A", problem_data={
        "format": "mcq", "correct_answer": "B",
        "knowledge_point_ids": [str(uuid4())],
    }))

    assert result["structured_data"]["is_correct"] is False


@pytest.mark.asyncio
async def test_mcq_case_insensitive():
    result = await assessor_node(_make_state(student_answer="b", problem_data={
        "format": "mcq", "correct_answer": "B",
        "knowledge_point_ids": [str(uuid4())],
    }))

    assert result["structured_data"]["is_correct"] is True


@pytest.mark.asyncio
async def test_mcq_whitespace_trimmed():
    result = await assessor_node(_make_state(student_answer=" B ", problem_data={
        "format": "mcq", "correct_answer": "B",
        "knowledge_point_ids": [str(uuid4())],
    }))

    assert result["structured_data"]["is_correct"] is True


@pytest.mark.asyncio
async def test_mcq_generates_knowledge_update():
    kp_id = str(uuid4())
    result = await assessor_node(_make_state(student_answer="B", problem_data={
        "format": "mcq", "correct_answer": "B",
        "knowledge_point_ids": [kp_id],
    }))

    updates = result["knowledge_updates"]
    assert len(updates) == 1
    assert updates[0]["is_correct"] is True
    assert updates[0]["fsrs_rating"] == 3


# ── Non-MCQ fallback ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_non_mcq_no_llm_fallback():
    with patch("app.agents.assessor_agent.is_llm_available", return_value=False):
        result = await assessor_node(_make_state(
            student_answer="My essay text",
            problem_data={"format": "essay", "knowledge_point_ids": [str(uuid4())]},
        ))

    assert "Answer recorded" in result["agent_response"]
    assert result["model_used"] == "none"


# ── Prompt selection tests ─────────────────────────────────────────────────


def test_error_diagnosis_prompt_for_math():
    assert _select_assessment_prompt("amc_math", "open") == "error_diagnosis"


def test_ket_writing_prompt():
    assert _select_assessment_prompt("ket_english", "essay") == "ket_writing"


def test_chn_writing_prompt():
    assert _select_assessment_prompt("chn_composition", "essay") == "chn_writing"


def test_poetry_dictation_prompt():
    assert _select_assessment_prompt("chn_poetry", "dictation") == "poetry_dictation"


def test_poetry_scoring_prompt():
    assert _select_assessment_prompt("chn_poetry", "open") == "poetry_scoring"
