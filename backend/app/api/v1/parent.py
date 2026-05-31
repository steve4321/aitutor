from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, func, select

from app.api.deps import DbSession, get_current_user
from app.models.learning import LearningSession
from app.models.user import ParentLink, StudentProfile, User
from app.schemas.report import WeeklyReport

router = APIRouter(prefix="/parent", tags=["parent"])


@router.get("/children/{student_id}/report", response_model=WeeklyReport)
async def get_child_report(
    student_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    link_result = await db.execute(
        select(ParentLink).where(
            and_(
                ParentLink.parent_id == current_user.id,
                ParentLink.student_id == student_id,
            )
        )
    )
    if link_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this student's report",
        )

    target_start = date.today() - timedelta(days=date.today().weekday())
    target_end = target_start + timedelta(days=7)
    dt_start = datetime.combine(target_start, datetime.min.time())
    dt_end = datetime.combine(target_end, datetime.min.time())

    agg = await db.execute(
        select(
            func.count(LearningSession.id),
            func.coalesce(func.sum(LearningSession.xp_earned), 0),
            func.coalesce(func.sum(LearningSession.duration_sec), 0),
            func.coalesce(func.sum(LearningSession.problems_total), 0),
            func.coalesce(func.sum(LearningSession.problems_correct), 0),
        ).where(
            and_(
                LearningSession.student_id == student_id,
                LearningSession.started_at >= dt_start,
                LearningSession.started_at < dt_end,
            )
        )
    )
    total_sessions, xp_sum, duration_sum, problems_total, problems_correct = agg.one()

    profile_result = await db.execute(
        select(StudentProfile.streak_days).where(
            StudentProfile.user_id == student_id
        )
    )
    streak_row = profile_result.one_or_none()
    streak_days = streak_row[0] if streak_row else 0

    return WeeklyReport(
        week_start=target_start,
        week_end=target_end - timedelta(days=1),
        total_sessions=total_sessions,
        total_problems=int(problems_total),
        total_correct=int(problems_correct),
        total_xp=int(xp_sum),
        total_time_minutes=int(duration_sum) // 60,
        streak_days=streak_days,
        mastery_changes={},
    )
