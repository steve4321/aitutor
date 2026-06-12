"""Assessor node: evaluates answers, scores essays, diagnoses errors."""
import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm, is_llm_available
from app.agents.prompts import get_system_prompt
from app.agents.state import AgentState
from app.agents.constants import MasteryConstants
from app.agents.evaluation_helpers import heuristic_evaluate

logger = logging.getLogger(__name__)


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
        result = heuristic_evaluate(
            answer=answer,
            correct_answer=problem.get("correct_answer"),
            problem_format=problem_format,
        )
        return {
            "agent_response": result["feedback"],
            "structured_data": {
                "is_correct": result["is_correct"],
                "evaluation_method": "heuristic_fallback",
                "confidence": result["confidence"],
            },
            "knowledge_updates": [
                _build_knowledge_update(state, result["is_correct"])
            ],
            "model_used": "none",
        }

    # Select prompt based on subject
    prompt_key = _select_assessment_prompt(subject, problem_format)
    student_work = _extract_student_work(state)
    prompt_vars = _get_assessor_prompt_vars(prompt_key, state, answer, student_work)
    system_prompt = get_system_prompt(prompt_key, **prompt_vars)

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


def _extract_student_work(state: AgentState) -> str:
    """Try to extract student work content from media attachments."""
    media = state.get("media")
    if media and isinstance(media, dict):
        if media.get("transcription"):
            return media["transcription"]
        if media.get("ocr_text"):
            return media["ocr_text"]
        if media.get("content"):
            return media["content"]
    return ""


def _get_assessor_prompt_vars(prompt_key: str, state: AgentState, answer: str, student_work: str) -> dict:
    """Build prompt variables for the assessor based on the selected prompt template."""
    problem = state.get("problem_data") or {}
    student = state.get("student") or {}
    base = {
        "student_answer": answer,
        "student_work": student_work,
    }

    if prompt_key == "ket_writing":
        base.update({
            "task_description": problem.get("question_markdown", ""),
            "required_points": ", ".join(problem.get("required_points", [])),
            "student_essay": answer,
        })
    elif prompt_key == "chn_writing":
        grade = student.get("grade_level", 5)
        grade_chars = {4: (200, 400, 300), 5: (300, 500, 400), 6: (350, 550, 450)}
        min_c, max_c, target_c = grade_chars.get(grade, (300, 500, 400))
        base.update({
            "task_description": problem.get("question_markdown", ""),
            "writing_type": problem.get("writing_type", problem.get("format", "记叙文")),
            "min_chars": problem.get("min_chars", min_c),
            "max_chars": problem.get("max_chars", max_c),
            "target_chars": problem.get("target_chars", target_c),
            "chn_grade": problem.get("grade", grade),
            "student_essay": answer,
        })
    elif prompt_key == "poetry_scoring":
        base.update({
            "question": problem.get("question_markdown", ""),
            "reference_points": ", ".join(problem.get("reference_points", problem.get("key_points", []))),
            "max_score": problem.get("max_score", problem.get("points", 10)),
        })
    elif prompt_key == "poetry_dictation":
        lesson_data = state.get("lesson_data") or {}
        content = lesson_data.get("content", {})
        base.update({
            "full_text": content.get("full_text", content.get("text", "")),
            "student_dictation": answer,
            "acceptable_variants": ", ".join(content.get("acceptable_variants", [])),
        })
    else:
        base.update({
            "problem": problem.get("question_markdown", ""),
            "correct_answer": problem.get("correct_answer", "N/A"),
        })

    return base


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
