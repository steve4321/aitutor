from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CompositionTaskResponse(BaseModel):
    id: UUID
    title: str
    writing_type: str
    prompt: str
    min_chars: int
    max_chars: int
    status: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PoetryResponse(BaseModel):
    id: UUID
    title: str
    poet: str
    dynasty: str
    theme: str
    mastery_status: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PoetryListResponse(BaseModel):
    items: list[PoetryResponse]
    total: int
