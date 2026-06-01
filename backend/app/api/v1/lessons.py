from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession
from app.models.course import Lesson
from app.schemas.course import LessonResponse

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: UUID, db: DbSession):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    return lesson


@router.post("/{lesson_id}/progress")
async def update_lesson_progress(lesson_id: UUID, db: DbSession):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    return {
        "lesson_id": str(lesson.id),
        "title": lesson.title,
        "progress": "in_progress",
        "status": "ok",
    }
