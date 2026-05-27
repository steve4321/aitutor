from uuid import UUID

from pydantic import BaseModel


class ChatMessageRequest(BaseModel):
    session_id: UUID | None = None
    content: str
    media: dict | None = None


class ChatMessageResponse(BaseModel):
    id: UUID
    role: str
    content: str

    model_config = {"from_attributes": True}
