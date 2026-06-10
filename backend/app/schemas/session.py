from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

SessionType = Literal["practice", "lesson", "review"]
SessionSubject = Literal["math", "english", "chinese"]


class SessionCreate(BaseModel):
    session_type: SessionType = "practice"
    subject: SessionSubject = "math"
    knowledge_point_id: UUID | None = None


class SessionResponse(BaseModel):
    id: UUID
    student_id: UUID
    session_type: str
    subject: str
    knowledge_point_id: UUID | None
    started_at: datetime
    ended_at: datetime | None
    duration_sec: int | None
    problems_total: int | None
    problems_correct: int | None
    score_pct: float | None
    xp_earned: int
    summary: str | None

    model_config = {"from_attributes": True}
