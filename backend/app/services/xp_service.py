import logging
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
