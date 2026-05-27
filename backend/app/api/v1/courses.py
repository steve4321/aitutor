from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.schemas.course import CourseResponse, LessonResponse

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseResponse])
async def list_courses(db: DbSession):
    ...


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: UUID, db: DbSession):
    ...


@router.get("/{course_id}/lessons", response_model=list[LessonResponse])
async def list_course_lessons(course_id: UUID, db: DbSession):
    ...
