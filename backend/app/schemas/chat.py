from uuid import UUID

from pydantic import BaseModel, Field


class ChatMessageRequest(BaseModel):
    session_id: UUID | None = None
    content: str = Field(..., min_length=1, max_length=4000)
    media: dict | None = None


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str
    session_id: UUID | None = None

    model_config = {"from_attributes": True}
