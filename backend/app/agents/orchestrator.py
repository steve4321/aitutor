"""Orchestrator node: loads student context and session data."""
import asyncio
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
    session_id = state.get("session_id")
    problem_id = state.get("problem_id")
    lesson_id = state.get("lesson_id")

    coroutines = []
    keys = []

    if student_id:
        sid = UUID(str(student_id))
        coroutines.append(load_student_context(db, sid))
        keys.append("student")
        coroutines.append(load_knowledge_states(db, sid))
        keys.append("knowledge_states")

    if session_id:
        coroutines.append(load_session_messages(db, UUID(str(session_id))))
        keys.append("session_messages")

    if problem_id:
        coroutines.append(load_problem(db, UUID(str(problem_id))))
        keys.append("problem_data")

    if lesson_id:
        coroutines.append(load_lesson(db, UUID(str(lesson_id))))
        keys.append("lesson_data")

    if coroutines:
        results = await asyncio.gather(*coroutines)
        for key, result in zip(keys, results):
            updates[key] = result

    return updates
