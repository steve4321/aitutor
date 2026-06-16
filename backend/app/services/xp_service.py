import logging
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

LESSON_XP_REWARD = 50
PROBLEM_XP_REWARD = 20


async def _build_achievement_stats(
    db: AsyncSession, user_id: UUID, profile
) -> dict:
    from app.models.learning import LearningSession, StudentAttempt

    lessons_result = await db.execute(
        select(func.count()).select_from(LearningSession).where(
            LearningSession.student_id == user_id,
            LearningSession.session_type == "lesson",
            LearningSession.ended_at.isnot(None),
        )
    )
    lessons_completed = lessons_result.scalar() or 0

    problems_result = await db.execute(
        select(func.count()).select_from(StudentAttempt).where(
            StudentAttempt.student_id == user_id,
            StudentAttempt.is_correct.is_(True),
        )
    )
    problems_correct = problems_result.scalar() or 0

    return {
        "lessons_completed": lessons_completed,
        "problems_correct": problems_correct,
        "streak_days": profile.streak_days or 0,
        "xp_total": profile.xp_total or 0,
    }


async def _check_achievements(db: AsyncSession, user_id: UUID, profile) -> None:
    from app.services.achievement_service import check_and_award

    try:
        stats = await _build_achievement_stats(db, user_id, profile)
        await check_and_award(db, user_id, stats)
    except Exception:
        logger.warning("Achievement check failed", exc_info=True)


async def award_lesson_xp(db: AsyncSession, user_id: UUID) -> int:
    from app.models.user import StudentProfile

    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return 0
    profile.xp_total = (profile.xp_total or 0) + LESSON_XP_REWARD
    await update_streak(db, user_id, profile=profile)
    await _check_achievements(db, user_id, profile)
    return LESSON_XP_REWARD


async def award_problem_xp(db: AsyncSession, user_id: UUID, is_correct: bool) -> int:
    if not is_correct:
        return 0
    from app.models.user import StudentProfile

    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        return 0
    profile.xp_total = (profile.xp_total or 0) + PROBLEM_XP_REWARD
    await update_streak(db, user_id, profile=profile)
    await _check_achievements(db, user_id, profile)
    return PROBLEM_XP_REWARD


async def update_streak(
    db: AsyncSession,
    user_id: UUID,
    profile=None,
) -> int:
    from app.models.user import StudentProfile

    if profile is None:
        result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
    if profile is None:
        return 0

    today = date.today()
    if profile.last_active_date == today:
        return profile.streak_days

    if profile.last_active_date == today - timedelta(days=1):
        profile.streak_days = (profile.streak_days or 0) + 1
    else:
        profile.streak_days = 1

    profile.longest_streak = max(profile.longest_streak or 0, profile.streak_days)
    profile.last_active_date = today
    return profile.streak_days
