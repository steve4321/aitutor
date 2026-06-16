from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class LinkedChild(BaseModel):
    id: UUID
    name: str
    grade_level: int | None
    target_exam: str | None
    streak_days: int
    xp_total: int
    linked_at: datetime


class ChildOverview(BaseModel):
    child_id: UUID
    child_name: str
    target_exam: str | None
    streak_days: int
    weekly_study_minutes: int
    weekly_goal_completion: int
    minutes_today: int
    daily_goal_minutes: int


class PillarMasteryValues(BaseModel):
    algebra: float
    geometry: float
    counting: float
    number_theory: float


class MasteryTrend(BaseModel):
    week_start: date
    pillars: PillarMasteryValues


class MasteryTrendsResponse(BaseModel):
    child_id: UUID
    trends: list[MasteryTrend]


class ParentNotificationItem(BaseModel):
    id: str
    type: str
    title: str
    message: str
    created_at: datetime
    read: bool
    metadata: dict | None = None


class NotificationsResponse(BaseModel):
    items: list[ParentNotificationItem]
    total: int
