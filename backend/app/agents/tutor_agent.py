"""Tutor node: core teaching conversation with subject-specific strategies."""
import logging

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agents.llm import get_llm, get_fallback_response, is_llm_available
from app.agents.prompts import get_system_prompt
from app.agents.state import AgentState

logger = logging.getLogger(__name__)


async def tutor_node(state: AgentState) -> dict:
    """Execute teaching conversation based on subject and mode."""

    if not is_llm_available():
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
        ("chn_poetry", "course"): "poetry_teaching",
    }
    prompt_key = mode_map.get((subject, session_mode), "math_socratic")

    system_prompt = get_system_prompt(
        prompt_key,
        student_name=student.get("name", "同学"),
        grade_level=student.get("grade_level", 5),
        target_exam=student.get("target_exam", "AMC8"),
        mastery_level=_get_mastery_summary(state),
        mastered_kps=", ".join(student.get("mastered_kps", [])[:10]),
        weak_areas=", ".join(student.get("weak_areas", [])[:5]),
        problem_markdown=_get_problem_text(state),
        correct_answer=_get_correct_answer(state),
        reference_solutions=_get_solutions(state),
        hint_level=state.get("hint_level", 0),
    )

    messages = [SystemMessage(content=system_prompt)]
    for msg in state.get("session_messages", [])[-10:]:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))

    messages.append(HumanMessage(content=state.get("user_message", "")))

    llm = get_llm("strong")
    response = await llm.ainvoke(messages)

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
