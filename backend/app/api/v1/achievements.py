from fastapi import APIRouter, Depends
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user
from app.models.achievement import Achievement
from app.models.user import User
from app.schemas.achievement import AchievementResponse

router = APIRouter(prefix="/achievements", tags=["achievements"])


@router.get("", response_model=list[AchievementResponse])
async def list_achievements(
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Achievement)
        .where(Achievement.student_id == current_user.id)
        .order_by(Achievement.earned_at.desc())
    )
    return list(result.scalars().all())
