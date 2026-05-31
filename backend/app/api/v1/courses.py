from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.api.deps import DbSession
from app.schemas.course import CourseResponse, LessonResponse, UnitResponse
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseResponse])
async def list_courses(db: DbSession, subject: str | None = None):
    courses = await course_service.get_courses(db, subject)
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: UUID, db: DbSession):
    course = await course_service.get_course_detail(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/{course_id}/units", response_model=list[UnitResponse])
async def list_units(course_id: UUID, db: DbSession):
    units = await course_service.get_course_units(db, course_id)
    return units


@router.get("/{course_id}/lessons", response_model=list[LessonResponse])
async def list_lessons(course_id: UUID, db: DbSession):
    lessons = await course_service.get_course_lessons(db, course_id)
    return lessons