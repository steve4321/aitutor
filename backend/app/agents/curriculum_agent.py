"""Curriculum node: course scheduling, recommendations, FSRS reviews."""
from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm, is_llm_available
from app.agents.state import AgentState
from app.agents.services.problem_selector import select_next_problem


async def curriculum_node(state: AgentState) -> dict:
    """
    Handle curriculum-related requests:
    - Session initialization (recommend starting point)
    - Next problem selection (adaptive)
    - Review scheduling (FSRS)
    - Progress summary
    """
    intent = state.get("intent", "manage")
    knowledge_states = state.get("knowledge_states", [])
    student = state.get("student", {})

    if intent == "manage" and state.get("request_type") == "session_init":
        return await _handle_session_init(state, knowledge_states, student)

    if intent == "practice":
        return await _handle_next_problem(state, knowledge_states, student)

    # General management/progress query
    return await _handle_general(state, knowledge_states, student)


async def _handle_session_init(state, knowledge_states, student) -> dict:
    """Recommend starting point for new session."""
    # Find FSRS-due reviews
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    due_reviews = [
        ks for ks in knowledge_states
        if ks.get("next_review") and
           datetime.fromisoformat(ks["next_review"]) <= now
    ]

    # Find weakest areas
    weak = [ks for ks in knowledge_states if ks["mastery"] < 0.4 and ks["mastery"] > 0]

    response_parts = []
    if due_reviews:
        response_parts.append(
            f"You have {len(due_reviews)} knowledge points due for review."
        )
    if weak:
        response_parts.append(
            "Your weakest areas need attention (mastery < 40%)."
        )

    message = " ".join(response_parts) if response_parts else (
        "Welcome! Let's find the right starting point for you."
    )

    return {
        "agent_response": message,
        "structured_data": {
            "due_reviews": len(due_reviews),
            "weak_areas": len(weak),
            "recommendation": "review" if due_reviews else "learn_new",
        },
    }


async def _handle_next_problem(state, knowledge_states, student) -> dict:
    """Select next problem based on adaptive strategy."""
    from app.db.session import async_session_factory
    from uuid import UUID

    student_id = state.get("student_id")
    subject = state.get("subject", "amc_math")
    target_exam = student.get("target_exam", "AMC8")

    async with async_session_factory() as db:
        problem = await select_next_problem(
            db=db,
            student_id=UUID(str(student_id)),
            subject=subject,
            target_exam=target_exam,
            knowledge_states=knowledge_states,
        )

    if problem:
        return {
            "agent_response": f"Here's your next problem:\n\n{problem.question_markdown}",
            "structured_data": {
                "next_problem_id": str(problem.id),
                "difficulty": problem.difficulty,
            },
        }

    return {
        "agent_response": "No more problems available for this topic right now. Try a different area!",
    }


async def _handle_general(state, knowledge_states, student) -> dict:
    """Handle general curriculum queries."""
    if not is_llm_available():
        return {
            "agent_response": "Curriculum features require an internet connection.",
        }

    # Build progress summary
    summary = _build_progress_summary(knowledge_states, student)
    user_msg = state.get("user_message", "Show my progress")

    llm = get_llm("fast")
    if llm is None:
        return {
            "agent_response": "Curriculum features require an internet connection.",
        }
    messages = [
        SystemMessage(content=f"You are a learning progress assistant.\n\nStudent progress:\n{summary}"),
        HumanMessage(content=user_msg),
    ]
    response = await llm.ainvoke(messages)

    return {
        "agent_response": response.content,
        "model_used": "fast",
    }


def _build_progress_summary(knowledge_states, student) -> str:
    """Build a text summary of student progress."""
    if not knowledge_states:
        return "No learning data yet."

    by_level = {}
    for ks in knowledge_states:
        level = ks.get("mastery_level", "unknown")
        by_level[level] = by_level.get(level, 0) + 1

    lines = [f"Student: {student.get('name', 'Unknown')}"]
    lines.append(f"Target: {student.get('target_exam', 'Not set')}")
    lines.append(f"Knowledge states: {len(knowledge_states)} tracked")
    for level, count in sorted(by_level.items()):
        lines.append(f"  {level}: {count}")

    return "\n".join(lines)
