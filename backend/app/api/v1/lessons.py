from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import func, select

from app.api.deps import DbSession, get_current_user
from app.models.course import Lesson, Unit
from app.models.enrollment import Enrollment
from app.models.user import User
from app.schemas.course import LessonResponse
from app.services import xp_service

router = APIRouter(prefix="/lessons", tags=["lessons"])


@router.get("/{lesson_id}", response_model=LessonResponse)
async def get_lesson(lesson_id: UUID, db: DbSession, current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lesson not found",
        )
    return lesson


class LessonProgressRequest(BaseModel):
    status: str  # "in_progress" | "completed"
    score: int | None = None


class LessonProgressResponse(BaseModel):
    message: str
    progress: int
    xp_earned: int = 0


@router.post("/{lesson_id}/progress", response_model=LessonProgressResponse)
async def update_lesson_progress(
    lesson_id: UUID,
    body: LessonProgressRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    lesson_result = await db.execute(
        select(Lesson).where(Lesson.id == lesson_id)
    )
    lesson = lesson_result.scalar_one_or_none()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    unit_result = await db.execute(select(Unit).where(Unit.id == lesson.unit_id))
    unit = unit_result.scalar_one_or_none()
    if unit is None:
        raise HTTPException(status_code=404, detail="Unit not found")

    enr_result = await db.execute(
        select(Enrollment).where(
            Enrollment.user_id == current_user.id,
            Enrollment.course_id == unit.course_id,
        )
    )
    enrollment = enr_result.scalar_one_or_none()
    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Must enroll in course before tracking progress",
        )

    xp_earned = 0
    if body.status == "completed":
        progress_pct = await _compute_course_progress(db, unit.course_id, current_user.id)
        enrollment.progress = progress_pct
        xp_earned = await xp_service.award_lesson_xp(db, current_user.id)

    return LessonProgressResponse(
        message="ok",
        progress=enrollment.progress,
        xp_earned=xp_earned,
    )


async def _compute_course_progress(db, course_id: UUID, user_id: UUID) -> int:
    """Count distinct lessons completed across all closed learning sessions for this user
    divided by total published lessons in the course, as a percentage 0-100.
    """
    from app.models.learning import LearningSession

    total_result = await db.execute(
        select(func.count(Lesson.id))
        .join(Unit, Lesson.unit_id == Unit.id)
        .where(Unit.course_id == course_id, Lesson.is_published.is_(True))
    )
    total = total_result.scalar() or 0
    if total == 0:
        return 0

    completed_result = await db.execute(
        select(func.count(func.distinct(LearningSession.lesson_id)))
        .where(
            LearningSession.student_id == user_id,
            LearningSession.lesson_id.isnot(None),
            LearningSession.ended_at.isnot(None),
            LearningSession.lesson_id.in_(
                select(Lesson.id).join(Unit, Lesson.unit_id == Unit.id).where(Unit.course_id == course_id)
            ),
        )
    )
    completed = completed_result.scalar() or 0
    return int((completed / total) * 100)
