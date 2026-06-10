from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.knowledge import KnowledgePoint
from app.models.learning import KnowledgeState, LearningSession
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


async def get_subject_breakdown(
    db: AsyncSession,
    student_id: UUID,
    start: datetime,
    end: datetime,
) -> dict[str, dict]:
    """Compute per-subject aggregated stats for sessions in [start, end)."""
    result = await db.execute(
        select(
            LearningSession.subject,
            func.count(LearningSession.id),
            func.coalesce(func.sum(LearningSession.problems_total), 0),
            func.coalesce(func.sum(LearningSession.problems_correct), 0),
            func.coalesce(func.sum(LearningSession.xp_earned), 0),
            func.coalesce(func.sum(LearningSession.duration_sec), 0),
        )
        .where(
            and_(
                LearningSession.student_id == student_id,
                LearningSession.started_at >= start,
                LearningSession.started_at < end,
            )
        )
        .group_by(LearningSession.subject)
    )
    breakdown: dict[str, dict] = {}
    for subject, sessions, problems, correct, xp, duration in result.all():
        breakdown[subject] = {
            "total_problems": int(problems),
            "total_correct": int(correct),
            "total_xp": int(xp),
            "total_time_minutes": int(duration) // 60,
            "sessions_count": sessions,
        }
    return breakdown


async def get_mastery_changes(
    db: AsyncSession,
    student_id: UUID,
    start: datetime,
    end: datetime,
) -> dict[str, float]:
    """Compute per-knowledge-point mastery delta in [start, end).

    Returns mapping of KP code → (current mastery − mastery at start of window).
    States that didn't exist at the start count as 0; states with no
    last_review in the window contribute their current mastery.
    """
    state_result = await db.execute(
        select(KnowledgeState).where(KnowledgeState.student_id == student_id)
    )
    states = state_result.scalars().all()
    if not states:
        return {}

    kp_ids = [s.knowledge_point_id for s in states]
    kp_result = await db.execute(
        select(KnowledgePoint).where(KnowledgePoint.id.in_(kp_ids))
    )
    kp_by_id = {kp.id: kp for kp in kp_result.scalars().all()}

    mastered_in_window = await db.execute(
        select(LearningSession.knowledge_point_id)
        .where(
            and_(
                LearningSession.student_id == student_id,
                LearningSession.started_at >= start,
                LearningSession.started_at < end,
                LearningSession.knowledge_point_id.isnot(None),
            )
        )
        .distinct()
    )
    kps_touched = {row[0] for row in mastered_in_window.all()}

    changes: dict[str, float] = {}
    for state in states:
        if state.knowledge_point_id not in kp_by_id:
            continue
        kp = kp_by_id[state.knowledge_point_id]
        baseline = 0.0
        if state.last_review and state.last_review < start:
            baseline = state.mastery
        if state.knowledge_point_id in kps_touched or state.last_review is None:
            changes[kp.code] = round(state.mastery - baseline, 4)
    return changes
