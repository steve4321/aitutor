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

    model_config = {"from_attributes": True}


class AttemptRequest(BaseModel):
    answer: str
    session_id: UUID | None = None
    time_spent_sec: int | None = None


class AttemptResponse(BaseModel):
    id: UUID
    is_correct: bool | None
    ai_feedback: str | None
    error_type: str | None = None
    attempt_number: int

    model_config = {"from_attributes": True}
