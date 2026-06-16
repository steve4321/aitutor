import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.gamification_service import (
    LESSON_XP_REWARD,
    PROBLEM_XP_REWARD,
    process_student_progress,
    update_streak as _update_streak,
)

logger = logging.getLogger(__name__)


async def award_lesson_xp(db: AsyncSession, user_id: UUID) -> int:
    result = await process_student_progress(db, user_id, LESSON_XP_REWARD)
    return result["xp_awarded"]


async def award_problem_xp(db: AsyncSession, user_id: UUID, is_correct: bool) -> int:
    if not is_correct:
        return 0
    result = await process_student_progress(db, user_id, PROBLEM_XP_REWARD)
    return result["xp_awarded"]


async def update_streak(
    db: AsyncSession,
    user_id: UUID,
    profile=None,
) -> int:
    return await _update_streak(db, user_id, profile=profile)
