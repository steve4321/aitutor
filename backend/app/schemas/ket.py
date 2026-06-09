from uuid import UUID
from datetime import datetime

from pydantic import BaseModel


class KETQuestionResponse(BaseModel):
    id: UUID
    skill: str
    level: str
    question_type: str
    prompt: str
    audio_url: str | None
    image_url: str | None
    options: dict | None
    correct_answer: str
    explanation: str | None
    points: int
    created_at: datetime

    model_config = {"from_attributes": True}


class KETQuestionListResponse(BaseModel):
    items: list[KETQuestionResponse]
    total: int
    limit: int
    offset: int


class KETWritingTaskResponse(BaseModel):
    id: UUID
    task_type: str
    prompt: str
    image_url: str | None
    word_limit_min: int
    word_limit_max: int
    sample_response: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class KETWritingSubmitRequest(BaseModel):
    task_id: UUID
    content: str
    word_count: int


class KETWritingScoreResponse(BaseModel):
    score: float
    content_score: float
    organization_score: float
    language_score: float
    feedback: str
    band: float


class KETSpeakingTaskResponse(BaseModel):
    id: UUID
    topic: str
    question: str
    difficulty: str
    expected_duration_sec: int
    created_at: datetime

    model_config = {"from_attributes": True}


class KETSpeakingSubmitRequest(BaseModel):
    task_id: UUID
    transcript: str
    audio_duration_sec: int


class KETSpeakingScoreResponse(BaseModel):
    score: float
    band: float
    feedback: str
