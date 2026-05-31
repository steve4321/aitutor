from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select

from app.api.deps import DbSession, get_current_user
from app.models.learning import LearningSession
from app.models.user import StudentProfile, User
from app.schemas.report import DailyReport, WeeklyReport

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily", response_model=DailyReport)
async def get_daily_report(
    db: DbSession,
    current_user: User = Depends(get_current_user),
    report_date: date | None = None,
):
    target_date = report_date or date.today()
    day_start = datetime.combine(target_date, datetime.min.time())
    day_end = datetime.combine(target_date + timedelta(days=1), datetime.min.time())

    agg = await db.execute(
        select(
            func.count(LearningSession.id),
            func.coalesce(func.sum(LearningSession.xp_earned), 0),
            func.coalesce(func.sum(LearningSession.duration_sec), 0),
            func.coalesce(func.sum(LearningSession.problems_total), 0),
            func.coalesce(func.sum(LearningSession.problems_correct), 0),
        ).where(
            and_(
                LearningSession.student_id == current_user.id,
                LearningSession.started_at >= day_start,
                LearningSession.started_at < day_end,
            )
        )
    )
    sessions_count, xp_sum, duration_sum, problems_total, problems_correct = agg.one()

    kp_result = await db.execute(
        select(LearningSession.knowledge_point_id).where(
            and_(
                LearningSession.student_id == current_user.id,
                LearningSession.started_at >= day_start,
                LearningSession.started_at < day_end,
                LearningSession.knowledge_point_id.isnot(None),
            )
        ).distinct()
    )
    knowledge_points = [row[0] for row in kp_result.all()]

    return DailyReport(
        date=target_date,
        sessions_count=sessions_count,
        problems_attempted=int(problems_total),
        problems_correct=int(problems_correct),
        xp_earned=int(xp_sum),
        time_spent_minutes=int(duration_sum) // 60,
        knowledge_points_reviewed=knowledge_points,
    )


@router.get("/weekly", response_model=WeeklyReport)
async def get_weekly_report(
    db: DbSession,
    current_user: User = Depends(get_current_user),
    week_start: date | None = None,
):
    target_start = week_start or (date.today() - timedelta(days=date.today().weekday()))
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
                LearningSession.student_id == current_user.id,
                LearningSession.started_at >= dt_start,
                LearningSession.started_at < dt_end,
            )
        )
    )
    total_sessions, xp_sum, duration_sum, problems_total, problems_correct = agg.one()

    profile_result = await db.execute(
        select(StudentProfile.streak_days).where(
            StudentProfile.user_id == current_user.id
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
