from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession, get_current_user
from app.models.user import User
from app.schemas.report import WeeklyReport

router = APIRouter(prefix="/parent", tags=["parent"])


@router.get("/children/{student_id}/report", response_model=WeeklyReport)
async def get_child_report(
    student_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    ...
