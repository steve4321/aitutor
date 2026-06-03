"""Orchestrator node: loads student context and session data."""
from uuid import UUID

from app.agents.state import AgentState
from app.agents.tools import (
    load_student_context,
    load_session_messages,
    load_knowledge_states,
    load_problem,
    load_lesson,
)
from app.db.session import async_session_factory  # kept for test compat; runtime uses state injection


async def orchestrator_node(state: AgentState) -> dict:
    """
    Entry node. Loads student profile, knowledge states,
    session messages, and problem/lesson data.
    """
    db = state.get("db_session")
    if db is None:
        async with async_session_factory() as db:
            return await _load_context(db, state)
    else:
        return await _load_context(db, state)


async def _load_context(db, state: AgentState) -> dict:
    updates: dict = {}
    student_id = state.get("student_id")
    if student_id:
        sid = UUID(str(student_id))
        updates["student"] = await load_student_context(db, sid)
        updates["knowledge_states"] = await load_knowledge_states(db, sid)

    session_id = state.get("session_id")
    if session_id:
        updates["session_messages"] = await load_session_messages(
            db, UUID(str(session_id))
        )

    problem_id = state.get("problem_id")
    if problem_id:
        updates["problem_data"] = await load_problem(db, UUID(str(problem_id)))

    lesson_id = state.get("lesson_id")
    if lesson_id:
        updates["lesson_data"] = await load_lesson(db, UUID(str(lesson_id)))

    return updates
