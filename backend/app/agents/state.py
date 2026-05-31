"""LangGraph Agent state definitions."""
from __future__ import annotations

from typing import TypedDict
from uuid import UUID


class StudentContext(TypedDict, total=False):
    """Student profile and knowledge state loaded by orchestrator."""
    student_id: UUID
    name: str
    grade_level: int | None
    target_exam: str | None
    preferred_lang: str
    diagnostic_done: bool
    mastered_kps: list[str]
    weak_areas: list[str]


class KnowledgeUpdate(TypedDict):
    """Pending knowledge state change to be committed."""
    knowledge_point_id: UUID
    mastery_delta: float
    is_correct: bool | None
    hint_level_used: int
    error_type: str | None
    fsrs_rating: int


class AgentState(TypedDict, total=False):
    """LangGraph state — flows through every node."""

    # Input (set by API endpoint)
    session_id: UUID
    student_id: UUID
    user_message: str
    media: dict | None
    request_type: str  # "chat" | "attempt" | "session_init" | "lesson_progress"

    # Problem context (for attempt requests)
    problem_id: UUID | None
    student_answer: str | None
    problem_data: dict | None

    # Lesson context (for course/lesson requests)
    lesson_id: UUID | None
    lesson_data: dict | None

    # Student context (loaded by orchestrator)
    student: StudentContext
    knowledge_states: list[dict]
    session_messages: list[dict]

    # Router output
    intent: str  # "learn" | "practice" | "assess" | "ask" | "manage"
    target_agent: str  # "tutor" | "assessor" | "curriculum"
    subject: str  # "amc_math" | "ket_english" | "chn_composition" | "chn_poetry"
    session_mode: str  # "course" | "practice" | "review" | "diagnostic"

    # Agent output
    agent_response: str
    structured_data: dict | None

    # Tracking
    hint_level: int
    knowledge_updates: list[KnowledgeUpdate]

    # Metadata
    model_used: str
    error: str | None


def initial_state(
    *,
    session_id: UUID,
    student_id: UUID,
    user_message: str,
    request_type: str = "chat",
    problem_id: UUID | None = None,
    student_answer: str | None = None,
    lesson_id: UUID | None = None,
    media: dict | None = None,
) -> AgentState:
    """Create initial state for a new graph invocation."""
    return {
        "session_id": session_id,
        "student_id": student_id,
        "user_message": user_message,
        "media": media,
        "request_type": request_type,
        "problem_id": problem_id,
        "student_answer": student_answer,
        "lesson_id": lesson_id,
        "hint_level": 0,
        "knowledge_updates": [],
    }
