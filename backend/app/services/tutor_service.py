"""Thin wrapper that delegates to the LangGraph agent pipeline."""

from app.agents import run_agent


async def generate_response(session_id, user_message, **kwargs) -> dict:
    """Generate an AI tutor response for the given session and message.

    This is a convenience wrapper around ``app.agents.run_agent`` so that
    higher-level service code can call it without importing from the agents
    package directly.

    Parameters
    ----------
    session_id : str | UUID
        The learning session ID.
    user_message : str
        The student's message.
    **kwargs
        Additional keyword arguments forwarded to ``run_agent`` (e.g.
        ``student_id``, ``request_type``, ``problem_id``).

    Returns
    -------
    dict
        The agent result containing ``agent_response``, ``structured_data``,
        and ``error`` keys.
    """
    return await run_agent(
        session_id=session_id,
        user_message=user_message,
        **kwargs,
    )
