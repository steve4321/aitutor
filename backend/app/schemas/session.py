from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class SessionCreate(BaseModel):
    session_type: str = "practice"  # practice, lesson, review
    subject: str = "math"
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
