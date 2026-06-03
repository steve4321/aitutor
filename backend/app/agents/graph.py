"""LangGraph StateGraph construction."""
import logging
from uuid import UUID

from langgraph.graph import END, StateGraph

from app.agents.assessor_agent import assessor_node
from app.agents.curriculum_agent import curriculum_node
from app.agents.orchestrator import orchestrator_node
from app.agents.router_agent import router_node
from app.agents.services.knowledge_tracker import apply_knowledge_updates
from app.agents.state import AgentState
from app.agents.tutor_agent import tutor_node
from app.db.session import async_session_factory  # kept for test compat; runtime uses state injection
from app.models.learning import StudentAttempt
from app.models.message import Message

logger = logging.getLogger(__name__)


def _route_after_router(state: AgentState) -> str:
    target = state.get("target_agent", "tutor")
    mapping = {
        "tutor": "tutor",
        "assessor": "assessor",
        "curriculum": "curriculum",
    }
    return mapping.get(target, "tutor")


async def _response_node(state: AgentState) -> dict:
    """Final node: persist messages, attempts, and knowledge updates to DB."""
    session_id = state.get("session_id")
    agent_response = state.get("agent_response", "")

    db = state.get("db_session")
    if db is None:
        async with async_session_factory() as db:
            return await _persist_response(db, state, session_id, agent_response)
    else:
        try:
            result = await _persist_response(db, state, session_id, agent_response)
            return result
        except Exception as e:
            logger.error(f"Failed to persist response: {e}", exc_info=True)
            return {"error": str(e)}


async def _persist_response(db, state, session_id, agent_response) -> dict:
    """Shared persistence logic."""
    # 1. Persist assistant message
    if agent_response and session_id:
        ai_msg = Message(
            session_id=UUID(str(session_id)),
            role="assistant",
            content=agent_response,
            metadata_={
                "model_used": state.get("model_used"),
                "intent": state.get("intent"),
                "target_agent": state.get("target_agent"),
            },
        )
        db.add(ai_msg)

    # 2. Persist student attempt (if assessment)
    if state.get("request_type") == "attempt":
        structured = state.get("structured_data", {})
        attempt = StudentAttempt(
            session_id=UUID(str(session_id)),
            student_id=UUID(str(state.get("student_id"))),
            problem_id=UUID(str(state.get("problem_id"))),
            answer=state.get("student_answer"),
            is_correct=structured.get("is_correct"),
            ai_feedback=agent_response,
            error_type=structured.get("error_type"),
            hint_level_used=state.get("hint_level", 0),
        )
        db.add(attempt)

    # 3. Apply knowledge state updates
    updates = state.get("knowledge_updates", [])
    if updates:
        await apply_knowledge_updates(
            db,
            student_id=UUID(str(state.get("student_id"))),
            updates=updates,
        )

    # Flush (not commit) when using injected session
    if state.get("db_session") is not None:
        await db.flush()
    else:
        await db.commit()

    return {}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("orchestrator", orchestrator_node)
    graph.add_node("router", router_node)
    graph.add_node("tutor", tutor_node)
    graph.add_node("assessor", assessor_node)
    graph.add_node("curriculum", curriculum_node)
    graph.add_node("response", _response_node)

    graph.set_entry_point("orchestrator")
    graph.add_edge("orchestrator", "router")
    graph.add_conditional_edges(
        "router",
        _route_after_router,
        {
            "tutor": "tutor",
            "assessor": "assessor",
            "curriculum": "curriculum",
        },
    )
    graph.add_edge("tutor", "response")
    graph.add_edge("assessor", "response")
    graph.add_edge("curriculum", "response")
    graph.add_edge("response", END)

    return graph.compile()
