"""Assessor node: evaluates answers, scores essays, diagnoses errors."""
import json
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm, is_llm_available
from app.agents.prompts import get_system_prompt
from app.agents.state import AgentState
from app.agents.constants import MasteryConstants


async def assessor_node(state: AgentState) -> dict:
    """Evaluate student answers with subject-specific rubrics."""

    problem = state.get("problem_data", {})
    subject = state.get("subject", "amc_math")
    answer = state.get("student_answer") or state.get("user_message", "")
    problem_format = problem.get("format", "mcq")

    # ── MCQ: exact match (no LLM needed) ─────────────────────
    if problem_format == "mcq" and problem.get("correct_answer"):
        correct = problem["correct_answer"].strip().upper()
        student_ans = answer.strip().upper()
        is_correct = (student_ans == correct)

        feedback = "Correct! Well done." if is_correct else (
            f"Not quite. The correct answer is {correct}."
        )

        return {
            "agent_response": feedback,
            "structured_data": {
                "is_correct": is_correct,
                "evaluation_method": "exact_match",
            },
            "knowledge_updates": [
                _build_knowledge_update(state, is_correct)
            ],
            "model_used": "none",
        }

    # ── Non-MCQ or complex formats: use LLM ──────────────────
    if not is_llm_available():
        # Fallback: basic heuristics
        is_correct = bool(answer.strip())
        return {
            "agent_response": "Answer recorded. AI feedback will be available later.",
            "structured_data": {
                "is_correct": is_correct,
                "evaluation_method": "fallback",
            },
            "knowledge_updates": [
                _build_knowledge_update(state, is_correct)
            ],
            "model_used": "none",
        }

    # Select prompt based on subject
    prompt_key = _select_assessment_prompt(subject, problem_format)
    system_prompt = get_system_prompt(
        prompt_key,
        problem=problem.get("question_markdown", ""),
        correct_answer=problem.get("correct_answer", "N/A"),
        student_answer=answer,
        student_work="",  # Could be extracted from media
    )

    llm = get_llm("strong")
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Student's answer: {answer}"),
    ]
    response = await llm.ainvoke(messages)

    # Parse structured response
    try:
        result = json.loads(response.content)
        is_correct = result.get("is_correct", False)

        return {
            "agent_response": result.get("feedback", response.content),
            "structured_data": result,
            "knowledge_updates": [
                _build_knowledge_update(state, is_correct, result.get("error_type"))
            ],
            "model_used": "strong",
        }
    except json.JSONDecodeError:
        return {
            "agent_response": response.content,
            "structured_data": {"is_correct": None, "evaluation_method": "llm_unstructured"},
            "knowledge_updates": [],
            "model_used": "strong",
        }


def _select_assessment_prompt(subject: str, problem_format: str) -> str:
    """Select the right assessment prompt."""
    if subject == "ket_english" and problem_format in ("essay", "email"):
        return "ket_writing"
    elif subject == "chn_composition":
        return "chn_writing"
    elif subject == "chn_poetry" and problem_format == "dictation":
        return "poetry_dictation"
    elif subject == "chn_poetry":
        return "poetry_scoring"
    else:
        return "error_diagnosis"


def _build_knowledge_update(
    state: AgentState,
    is_correct: bool,
    error_type: str | None = None,
) -> dict:
    """Build a KnowledgeUpdate for the problem's knowledge points."""
    problem = state.get("problem_data", {})
    kp_ids = problem.get("knowledge_point_ids", [])

    return {
        "knowledge_point_id": kp_ids[0] if kp_ids else None,
        "mastery_delta": MasteryConstants.INCREMENT_CORRECT if is_correct else -MasteryConstants.DECREMENT_INCORRECT,
        "is_correct": is_correct,
        "hint_level_used": state.get("hint_level", 0),
        "error_type": error_type,
        "fsrs_rating": 3 if is_correct else 1,
    }
