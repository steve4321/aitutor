from uuid import UUID

from pydantic import BaseModel


class ProblemResponse(BaseModel):
    id: UUID
    source: str | None
    subject: str
    format: str
    question_markdown: str
    options: dict | None
    difficulty: int | None
    estimated_time_sec: int | None
    hints: list[str] | None = None
    correct_answer: str | None = None
    knowledge_point_ids: list[str] | None = None
    explanation: str | None = None

    model_config = {"from_attributes": True}


class AttemptRequest(BaseModel):
    answer: str
    session_id: UUID | None = None
    time_spent_sec: int | None = None
    hint_level: int = 0


class AttemptResponse(BaseModel):
    id: UUID
    is_correct: bool | None
    ai_feedback: str | None
    error_type: str | None = None
    attempt_number: int
    xp_earned: int = 0

    model_config = {"from_attributes": True}
