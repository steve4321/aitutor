"""Heuristic evaluation helpers for when LLM is unavailable."""

from __future__ import annotations

import re


def heuristic_evaluate(
    answer: str,
    correct_answer: str | None = None,
    problem_format: str = "free_response",
) -> dict:
    """Return a best-effort evaluation without an LLM.

    Returns dict with keys: is_correct, feedback, confidence.
    """
    answer_stripped = (answer or "").strip()
    correct_stripped = (correct_answer or "").strip()

    dispatch = {
        "fill_in_blank": _eval_exact,
        "numeric": _eval_exact,
        "free_response": _eval_free_response,
        "short_answer": _eval_free_response,
        "essay": _eval_essay,
        "email": _eval_essay,
        "long_answer": _eval_essay,
    }

    handler = dispatch.get(problem_format)
    if handler:
        return handler(answer_stripped, correct_stripped)

    return _eval_default(answer_stripped)


def _token_overlap(answer: str, reference: str) -> float:
    """Fraction of reference tokens found in the answer (case-insensitive)."""
    if not reference:
        return 0.0
    ref_tokens = set(re.findall(r"\w+", reference.lower()))
    if not ref_tokens:
        return 0.0
    ans_tokens = set(re.findall(r"\w+", answer.lower()))
    return len(ref_tokens & ans_tokens) / len(ref_tokens)


def _eval_exact(answer: str, correct: str) -> dict:
    """fill_in_blank / numeric: exact or near-exact match."""
    if not answer:
        return dict(is_correct=False, feedback="No answer provided.", confidence=1.0)

    ans_norm = answer.lower()
    cor_norm = correct.lower()

    if ans_norm == cor_norm:
        return dict(is_correct=True, feedback="Correct!", confidence=0.95)

    # Partial credit: answer is contained in correct or vice-versa
    if cor_norm and (ans_norm in cor_norm or cor_norm in ans_norm):
        return dict(
            is_correct=True,
            feedback="Auto-evaluated: your answer is close to the expected answer. Full AI evaluation pending.",
            confidence=0.5,
        )

    return dict(
        is_correct=False,
        feedback="Auto-evaluated: answer does not match expected response. Full AI evaluation pending.",
        confidence=0.6,
    )


def _eval_free_response(answer: str, correct: str) -> dict:
    """free_response / short_answer: keyword overlap + length check."""
    if not answer:
        return dict(is_correct=False, feedback="No answer provided.", confidence=1.0)

    length = len(answer)
    overlap = _token_overlap(answer, correct)

    if length < 5:
        return dict(
            is_correct=False,
            feedback="Auto-evaluated: answer appears too short. Please provide a more complete response.",
            confidence=0.7,
        )

    is_correct = overlap > 0.5 and length > 10

    if is_correct:
        feedback = "Auto-evaluated: your answer covers the key concepts. Full AI evaluation pending."
    elif overlap > 0.25:
        feedback = "Auto-evaluated: your answer covers some key concepts but may be incomplete. Full AI evaluation pending."
    else:
        feedback = "Auto-evaluated: your answer may be missing key concepts. Full AI evaluation pending."

    return dict(is_correct=is_correct, feedback=feedback, confidence=0.5)


def _eval_essay(answer: str, _correct: str) -> dict:
    """essay / email / long_answer: structure and substance check."""
    if not answer:
        return dict(is_correct=False, feedback="No answer provided.", confidence=1.0)

    words = answer.split()
    word_count = len(words)
    sentences = len(re.findall(r"[.!?。！？]", answer))
    is_substantial = word_count >= 50 and sentences >= 3
    is_adequate = word_count >= 20 and sentences >= 1

    if is_substantial:
        return dict(
            is_correct=True,
            feedback=f"Auto-evaluated: substantive response ({word_count} words, {sentences} sentences). Full AI evaluation pending.",
            confidence=0.5,
        )

    if is_adequate:
        return dict(
            is_correct=True,
            feedback=f"Auto-evaluated: adequate response ({word_count} words). Consider elaborating further. Full AI evaluation pending.",
            confidence=0.4,
        )

    return dict(
        is_correct=False,
        feedback=f"Auto-evaluated: response is too brief ({word_count} words). Please provide a more detailed answer. Full AI evaluation pending.",
        confidence=0.6,
    )


def _eval_default(answer: str) -> dict:
    """Default fallback for unknown formats — optimistic for substantial answers."""
    if not answer or len(answer) <= 10:
        return dict(
            is_correct=False,
            feedback="Answer recorded. Detailed AI feedback will be available later.",
            confidence=0.3,
        )

    return dict(
        is_correct=True,
        feedback="Answer recorded. Detailed AI feedback will be available later.",
        confidence=0.3,
    )
