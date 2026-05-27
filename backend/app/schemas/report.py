from datetime import date
from uuid import UUID

from pydantic import BaseModel


class DailyReport(BaseModel):
    date: date
    sessions_count: int
    problems_attempted: int
    problems_correct: int
    xp_earned: int
    time_spent_minutes: int
    knowledge_points_reviewed: list[UUID]


class WeeklyReport(BaseModel):
    week_start: date
    week_end: date
    total_sessions: int
    total_problems: int
    total_correct: int
    total_xp: int
    total_time_minutes: int
    streak_days: int
    mastery_changes: dict[str, float]
