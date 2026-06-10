from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import and_, select

from app.api.deps import DbSession, get_current_user
from app.models.learning import LearningSession
from app.models.user import User
from app.schemas.report import DailyReport, WeeklyReport
from app.services import report_service

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

    agg = await report_service.aggregate_sessions(db, current_user.id, day_start, day_end)

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
        sessions_count=agg["total_sessions"],
        problems_attempted=agg["total_problems"],
        problems_correct=agg["total_correct"],
        xp_earned=agg["total_xp"],
        time_spent_minutes=agg["total_time_minutes"],
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

    agg = await report_service.aggregate_sessions(db, current_user.id, dt_start, dt_end)
    streak_days = await report_service.get_streak_days(db, current_user.id)
    mastery_changes = await report_service.get_mastery_changes(
        db, current_user.id, dt_start, dt_end
    )
    subject_breakdown = await report_service.get_subject_breakdown(
        db, current_user.id, dt_start, dt_end
    )

    return WeeklyReport(
        week_start=target_start,
        week_end=target_end - timedelta(days=1),
        total_sessions=agg["total_sessions"],
        total_problems=agg["total_problems"],
        total_correct=agg["total_correct"],
        total_xp=agg["total_xp"],
        total_time_minutes=agg["total_time_minutes"],
        streak_days=streak_days,
        mastery_changes=mastery_changes,
        subject_breakdown=subject_breakdown,
    )
