from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.schemas.course import LessonResponse

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: UUID, db: DbSession):
    ...


@router.post("/{lesson_id}/progress")
async def update_lesson_progress(lesson_id: UUID, db: DbSession):
    ...
