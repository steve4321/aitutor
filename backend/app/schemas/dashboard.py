from uuid import UUID

from pydantic import BaseModel


class DailyTaskItem(BaseModel):
    id: str
    title: str
    type: str
    xp: int
    completed: bool
    knowledge_point_id: UUID | None = None
    lesson_id: UUID | None = None


class DailyTasksResponse(BaseModel):
    tasks: list[DailyTaskItem]
    total_xp_available: int
    completed_count: int


class PillarMastery(BaseModel):
    name: str
    mastery: float
    color: str


class MasterySummaryResponse(BaseModel):
    subjects: list[PillarMastery]
    overall_mastery: float


class StreakResponse(BaseModel):
    current_streak: int
    longest_streak: int
    week_data: list[bool]
    total_xp: int
    daily_goal_minutes: int


class DashboardSummaryResponse(BaseModel):
    daily_tasks: DailyTasksResponse
    mastery_summary: MasterySummaryResponse
    streak: StreakResponse
