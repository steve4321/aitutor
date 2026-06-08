import logging
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

LESSON_XP_REWARD = 50
PROBLEM_XP_REWARD = 20


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
    return PROBLEM_XP_REWARD


async def update_streak(
    db: AsyncSession,
    user_id: UUID,
    profile=None,
) -> int:
    """Update streak count based on last_active_date.

    Logic:
    - If last_active_date is None: streak = 1
    - If last_active_date == today: no change
    - If last_active_date == yesterday: streak += 1
    - Else: streak = 1 (broken)
    """
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
