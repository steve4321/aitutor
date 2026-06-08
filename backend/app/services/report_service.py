from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning import LearningSession
from app.models.user import StudentProfile


async def aggregate_sessions(
    db: AsyncSession,
    student_id: UUID,
    start: datetime,
    end: datetime,
) -> dict:
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
                LearningSession.started_at >= start,
                LearningSession.started_at < end,
            )
        )
    )
    total_sessions, xp_sum, duration_sum, problems_total, problems_correct = agg.one()
    return {
        "total_sessions": total_sessions,
        "total_xp": int(xp_sum),
        "total_time_minutes": int(duration_sum) // 60,
        "total_problems": int(problems_total),
        "total_correct": int(problems_correct),
    }


async def get_streak_days(db: AsyncSession, student_id: UUID) -> int:
    result = await db.execute(
        select(StudentProfile.streak_days).where(
            StudentProfile.user_id == student_id
        )
    )
    row = result.one_or_none()
    return row[0] if row else 0
