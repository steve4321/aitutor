import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement
from app.services.gamification_service import award_achievements

logger = logging.getLogger(__name__)


async def check_and_award(
    db: AsyncSession, user_id: UUID, stats: dict
) -> list[Achievement]:
    return await award_achievements(db, user_id, stats)
