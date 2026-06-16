"""Tutor node: core teaching conversation with subject-specific strategies."""
import json
import logging
from collections.abc import Callable
from uuid import UUID

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.llm import get_llm, get_fallback_response, is_llm_available, llm_circuit_breaker
from app.agents.prompts import get_system_prompt
from app.agents.services.memory import (
    build_prerequisite_context,
    build_student_memory_context,
)
from app.agents.state import AgentState

logger = logging.getLogger(__name__)


async def tutor_node(state: AgentState) -> dict:
    """Execute teaching conversation based on subject and mode."""

    if not is_llm_available() or not llm_circuit_breaker.allow_call():
        return {
            "agent_response": get_fallback_response(state.get("intent", "learn")),
            "model_used": "none",
        }

    subject = state.get("subject", "amc_math")
    session_mode = state.get("session_mode", "practice")
    student = state.get("student", {})

    mode_map = {
        ("amc_math", "practice"): "math_socratic",
        ("amc_math", "course"): "math_course",
        ("amc_math", "review"): "amc_math_review",
        ("amc_math", "diagnostic"): "amc_math_diagnostic",
        ("ket_english", "course"): "ket_writing",
        ("ket_english", "practice"): "ket_writing",
        ("ket_english", "review"): "ket_writing",
        ("ket_english", "diagnostic"): "ket_writing",
        ("ket_english", "speaking"): "ket_speaking",
        ("chn_composition", "course"): "chn_writing",
        ("chn_composition", "practice"): "chn_writing",
        ("chn_composition", "review"): "chn_writing",
        ("chn_composition", "diagnostic"): "chn_writing",
        ("chn_poetry", "course"): "poetry_teaching",
        ("chn_poetry", "practice"): "chn_poetry_practice",
        ("chn_poetry", "review"): "poetry_teaching",
        ("chn_poetry", "diagnostic"): "poetry_scoring",
    }
    prompt_key = mode_map.get((subject, session_mode), "math_socratic")

    student_memory_context = await _load_student_memory_context(state, subject)
    prerequisite_context = await _load_prerequisite_context(state)

    base_vars = {
        "student_name": student.get("name", "同学"),
        "grade_level": student.get("grade_level", 5),
        "target_exam": student.get("target_exam", "AMC8"),
        "mastery_level": _get_mastery_summary(state),
        "mastered_kps": ", ".join(student.get("mastered_kps", [])[:10]),
        "weak_areas": ", ".join(student.get("weak_areas", [])[:5]),
        "problem_markdown": _get_problem_text(state),
        "correct_answer": _get_correct_answer(state),
        "reference_solutions": _get_solutions(state),
        "hint_level": state.get("hint_level", 0),
        "student_memory_context": student_memory_context,
        "prerequisite_context": prerequisite_context,
    }

    base_vars.update(_get_subject_prompt_vars(prompt_key, state))

    system_prompt = get_system_prompt(prompt_key, **base_vars)

    messages = [SystemMessage(content=system_prompt)]
    for msg in state.get("session_messages", [])[-10:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=state.get("user_message", "")))

    llm = get_llm("strong")
    if llm is None:
        return {
            "agent_response": get_fallback_response(state.get("intent", "learn")),
            "model_used": "none",
        }
    try:
        response = await llm.ainvoke(messages)
        llm_circuit_breaker.record_success()
    except Exception:
        llm_circuit_breaker.record_failure()
        logger.warning("LLM invocation failed in tutor_node", exc_info=True)
        return {
            "agent_response": get_fallback_response(state.get("intent", "learn")),
            "model_used": "none",
        }

    return {
        "agent_response": response.content,
        "model_used": "strong",
        "hint_level": state.get("hint_level", 0),
    }


def _get_mastery_summary(state: AgentState) -> str:
    kstates = state.get("knowledge_states", [])
    if not kstates:
        return "新学生，尚无掌握度数据"
    levels = [ks["mastery_level"] for ks in kstates[:5]]
    return f"最近知识点掌握度: {', '.join(levels)}"


async def _load_student_memory_context(state: AgentState, subject: str) -> str:
    """Load cross-session student memory context, if any recent summaries exist."""
    if not state.get("recent_summaries"):
        return "（暂无长期学习数据）"
    db = state.get("db_session")
    student_id = state.get("student_id")
    if db is None or student_id is None:
        return "（暂无长期学习数据）"
    try:
        return await build_student_memory_context(
            db=db,
            student_id=UUID(str(student_id)),
            subject=subject,
            summary_limit=3,
        )
    except Exception as e:
        logger.warning("Failed to build student memory context: %s", e)
        return "（暂无长期学习数据）"


async def _load_prerequisite_context(state: AgentState) -> str:
    """Build prerequisite chain context for the current lesson/problem."""
    db = state.get("db_session")
    student_id = state.get("student_id")
    if db is None or student_id is None:
        return ""

    lesson_data = state.get("lesson_data") or {}
    problem_data = state.get("problem_data") or {}
    kp_id = lesson_data.get("knowledge_point_id")
    if not kp_id:
        kp_ids = problem_data.get("knowledge_point_ids") or []
        kp_id = kp_ids[0] if kp_ids else None
    if not kp_id:
        return ""

    try:
        return await build_prerequisite_context(
            db=db,
            student_id=UUID(str(student_id)),
            current_kp_id=UUID(str(kp_id)),
        )
    except Exception as e:
        logger.warning("Failed to build prerequisite context: %s", e)
        return ""


def _vars_math_course(state: AgentState) -> dict:
    content = (state.get("lesson_data") or {}).get("content", {})
    return {
        "knowledge_point_name": content.get("knowledge_point_name", (state.get("lesson_data") or {}).get("title", "未知知识点")),
        "lesson_content_json": json.dumps(content, ensure_ascii=False) if content else "无课程内容",
        "current_step": (state.get("lesson_data") or {}).get("current_step", "introduction"),
    }


def _vars_ket_writing(state: AgentState) -> dict:
    problem_data = state.get("problem_data") or {}
    return {
        "task_description": problem_data.get("question_markdown", ""),
        "required_points": ", ".join(problem_data.get("required_points", [])),
        "student_essay": state.get("user_message", ""),
    }


def _vars_chn_writing(state: AgentState) -> dict:
    student = state.get("student") or {}
    problem_data = state.get("problem_data") or {}
    grade = student.get("grade_level", 5)
    grade_chars = {4: (200, 400, 300), 5: (300, 500, 400), 6: (350, 550, 450)}
    min_c, max_c, target_c = grade_chars.get(grade, (300, 500, 400))
    return {
        "task_description": problem_data.get("question_markdown", ""),
        "writing_type": problem_data.get("writing_type", problem_data.get("format", "记叙文")),
        "min_chars": problem_data.get("min_chars", min_c),
        "max_chars": problem_data.get("max_chars", max_c),
        "target_chars": problem_data.get("target_chars", target_c),
        "chn_grade": problem_data.get("grade", grade),
        "student_essay": state.get("user_message", ""),
    }


def _poetry_common_vars(state: AgentState) -> dict:
    content = (state.get("lesson_data") or {}).get("content", {})
    student = state.get("student") or {}
    return {
        "poem_title": content.get("title", content.get("poem_title", "未知")),
        "poet": content.get("poet", "未知"),
        "dynasty": content.get("dynasty", "未知"),
        "full_text": content.get("full_text", content.get("text", "")),
        "chn_grade": student.get("grade_level", 5),
        "learned_poems": ", ".join(student.get("learned_poems", [])),
        "mastered_imagery": ", ".join(student.get("mastered_imagery", [])),
    }


def _vars_poetry_teaching(state: AgentState) -> dict:
    lesson_data = state.get("lesson_data") or {}
    return {
        **_poetry_common_vars(state),
        "current_phase": lesson_data.get("current_step", lesson_data.get("current_phase", "read_poem")),
    }


def _vars_poetry_scoring(state: AgentState) -> dict:
    problem_data = state.get("problem_data") or {}
    return {
        "question": problem_data.get("question_markdown", ""),
        "reference_points": ", ".join(problem_data.get("reference_points", problem_data.get("key_points", []))),
        "student_answer": state.get("user_message", ""),
        "max_score": problem_data.get("max_score", problem_data.get("points", 10)),
    }


def _vars_ket_speaking(state: AgentState) -> dict:
    problem_data = state.get("problem_data") or {}
    return {
        "speaking_phase": problem_data.get("speaking_phase", "part1_warmup"),
        "student_response": state.get("user_message", ""),
        "asr_transcript": problem_data.get("asr_transcript", ""),
    }


def _vars_chn_poetry_practice(state: AgentState) -> dict:
    problem_data = state.get("problem_data") or {}
    return {
        **_poetry_common_vars(state),
        "practice_mode": problem_data.get("practice_mode", "dictation"),
        "practice_question": problem_data.get("question_markdown", ""),
        "student_answer": state.get("user_message", ""),
        "max_score": problem_data.get("max_score", problem_data.get("points", 10)),
    }


def _vars_amc_math_review(state: AgentState) -> dict:
    review_data = state.get("review_data") or {}
    return {
        "review_schedule": review_data.get("schedule_summary", "按FSRS调度安排复习"),
        "due_knowledge_points": ", ".join(review_data.get("due_knowledge_points", [])),
        "review_history": review_data.get("history_summary", "暂无历史复习记录"),
    }


def _vars_amc_math_diagnostic(state: AgentState) -> dict:
    diagnostic_data = state.get("diagnostic_data") or {}
    return {
        "diagnostic_progress": diagnostic_data.get("progress", 1),
        "student_answer": state.get("user_message", ""),
    }


_PROMPT_VAR_EXTRACTORS: dict[str, Callable[[AgentState], dict]] = {
    "math_course": _vars_math_course,
    "ket_writing": _vars_ket_writing,
    "chn_writing": _vars_chn_writing,
    "poetry_teaching": _vars_poetry_teaching,
    "poetry_scoring": _vars_poetry_scoring,
    "ket_speaking": _vars_ket_speaking,
    "chn_poetry_practice": _vars_chn_poetry_practice,
    "amc_math_review": _vars_amc_math_review,
    "amc_math_diagnostic": _vars_amc_math_diagnostic,
}


def _get_subject_prompt_vars(prompt_key: str, state: AgentState) -> dict:
    extractor = _PROMPT_VAR_EXTRACTORS.get(prompt_key)
    return extractor(state) if extractor else {}


def _get_problem_text(state: AgentState) -> str:
    problem = state.get("problem_data")
    if problem:
        return problem.get("question_markdown", "无题目")
    return "当前无题目（对话模式）"


def _get_correct_answer(state: AgentState) -> str:
    problem = state.get("problem_data")
    if problem:
        return problem.get("correct_answer", "N/A")
    return "N/A"


def _get_solutions(state: AgentState) -> str:
    problem = state.get("problem_data")
    if problem and problem.get("solutions"):
        sols = []
        for s in problem["solutions"]:
            sol_text = f"方法: {s.get('method_name', '标准解法')}\n"
            sol_text += s.get("solution_markdown", "")
            sols.append(sol_text)
        return "\n---\n".join(sols)
    return "无参考解法"
