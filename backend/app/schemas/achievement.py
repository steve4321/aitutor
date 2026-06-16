from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AchievementResponse(BaseModel):
    id: UUID
    code: str
    title: str
    description: str | None
    earned_at: datetime

    model_config = {"from_attributes": True}
