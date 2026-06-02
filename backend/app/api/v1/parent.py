from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select

from app.api.deps import DbSession, get_current_user
from app.models.user import ParentLink, User
from app.schemas.report import WeeklyReport
from app.services import report_service

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

    agg = await report_service.aggregate_sessions(db, student_id, dt_start, dt_end)
    streak_days = await report_service.get_streak_days(db, student_id)

    return WeeklyReport(
        week_start=target_start,
        week_end=target_end - timedelta(days=1),
        total_sessions=agg["total_sessions"],
        total_problems=agg["total_problems"],
        total_correct=agg["total_correct"],
        total_xp=agg["total_xp"],
        total_time_minutes=agg["total_time_minutes"],
        streak_days=streak_days,
        mastery_changes={},
    )
