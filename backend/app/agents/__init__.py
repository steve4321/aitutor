"""Public API for the agent layer."""
from app.agents.graph import build_graph
from app.agents.state import initial_state

_compiled_graph = None


def get_graph():
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = build_graph()
    return _compiled_graph


async def run_agent(*, db_session, **kwargs) -> dict:
    state = initial_state(**kwargs, db_session=db_session)
    graph = get_graph()
    result = await graph.ainvoke(state)
    return {
        "agent_response": result.get("agent_response", ""),
        "structured_data": result.get("structured_data"),
        "error": result.get("error"),
        "message_id": result.get("message_id"),
    }
