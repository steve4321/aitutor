from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.schemas.report import DailyReport, WeeklyReport

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/daily", response_model=DailyReport)
async def get_daily_report(
    db: DbSession,
    report_date: date | None = None,
):
    ...


@router.get("/weekly", response_model=WeeklyReport)
async def get_weekly_report(
    db: DbSession,
    week_start: date | None = None,
):
    ...
