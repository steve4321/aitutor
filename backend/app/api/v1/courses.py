from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.course import CourseResponse, LessonResponse, UnitResponse
from app.services import course_service

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=list[CourseResponse])
async def list_courses(db: DbSession, current_user: User = Depends(get_current_user), subject: str | None = None):
    courses = await course_service.get_courses(db, subject)
    return courses


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: UUID, db: DbSession, current_user: User = Depends(get_current_user)):
    course = await course_service.get_course_detail(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.get("/{course_id}/units", response_model=list[UnitResponse])
async def list_units(course_id: UUID, db: DbSession, current_user: User = Depends(get_current_user)):
    units = await course_service.get_course_units(db, course_id)
    return units


@router.get("/{course_id}/lessons", response_model=list[LessonResponse])
async def list_lessons(course_id: UUID, db: DbSession, current_user: User = Depends(get_current_user)):
    lessons = await course_service.get_course_lessons(db, course_id)
    return lessons


class EnrollResponse(BaseModel):
    message: str
    enrollment_id: UUID


@router.post("/{course_id}/enroll", response_model=EnrollResponse, status_code=status.HTTP_201_CREATED)
async def enroll_in_course(
    course_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    course_result = await db.execute(select(Course).where(Course.id == course_id))
    if course_result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Course not found")

    existing = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == course_id,
        )
    )
    existing_enr = existing.scalar_one_or_none()
    if existing_enr:
        if not existing_enr.is_active:
            existing_enr.is_active = True
        return EnrollResponse(
            message="Already enrolled",
            enrollment_id=existing_enr.id,
        )

    enrollment = Enrollment(
        user_id=current_user.id,
        course_id=course_id,
        is_active=True,
        progress=0,
    )
    db.add(enrollment)
    await db.flush()
    return EnrollResponse(
        message="Enrolled successfully",
        enrollment_id=enrollment.id,
    )
