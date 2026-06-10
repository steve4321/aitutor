from uuid import UUID

from pydantic import BaseModel


class CourseResponse(BaseModel):
    id: UUID
    code: str | None
    subject: str
    name: str
    description: str | None
    target_exam: str | None
    estimated_hours: int | None
    is_published: bool

    model_config = {"from_attributes": True}


class UnitResponse(BaseModel):
    id: UUID
    course_id: UUID
    code: str | None
    name: str
    description: str | None
    sort_order: int
    required_mastery: float

    model_config = {"from_attributes": True}


class LessonResponse(BaseModel):
    id: UUID
    unit_id: UUID
    knowledge_point_id: UUID | None
    code: str | None
    title: str
    lesson_type: str | None
    estimated_minutes: int | None
    sort_order: int
    is_published: bool
    content: dict | None = None

    model_config = {"from_attributes": True}
