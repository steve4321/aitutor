from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import and_, func, select

from app.api.deps import DbSession, get_current_user
from app.models.course import Lesson
from app.models.knowledge import KnowledgePoint
from app.models.learning import KnowledgeState, LearningSession
from app.models.user import StudentProfile, User
from app.schemas.dashboard import (
    DailyTasksResponse,
    DailyTaskItem,
    DashboardSummaryResponse,
    MasterySummaryResponse,
    PillarMastery,
    StreakResponse,
)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

PILLAR_COLORS = {
    "Algebra": "#3b82f6",
    "Geometry": "#10b981",
    "Number Theory": "#f59e0b",
    "Counting & Probability": "#ef4444",
    "Reading": "#8b5cf6",
    "Writing": "#ec4899",
    "Listening": "#06b6d4",
    "Speaking": "#f97316",
}

DEFAULT_COLOR = "#6b7280"


def _today_range():
    today = date.today()
    return (
        datetime.combine(today, datetime.min.time()),
        datetime.combine(today + timedelta(days=1), datetime.min.time()),
    )


def _week_range():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    return (
        datetime.combine(monday, datetime.min.time()),
        datetime.combine(monday + timedelta(days=7), datetime.min.time()),
    )


async def _get_daily_tasks(db, student_id: UUID) -> DailyTasksResponse:
    day_start, day_end = _today_range()

    completed_session_kps = await db.execute(
        select(LearningSession.knowledge_point_id).where(
            and_(
                LearningSession.student_id == student_id,
                LearningSession.started_at >= day_start,
                LearningSession.started_at < day_end,
                LearningSession.knowledge_point_id.isnot(None),
            )
        ).distinct()
    )
    completed_kp_ids = {row[0] for row in completed_session_kps.all()}

    now = datetime.now()
    due_reviews_result = await db.execute(
        select(KnowledgeState, KnowledgePoint)
        .join(KnowledgePoint, KnowledgeState.knowledge_point_id == KnowledgePoint.id)
        .where(
            and_(
                KnowledgeState.student_id == student_id,
                KnowledgeState.next_review.isnot(None),
                KnowledgeState.next_review <= now,
                KnowledgeState.review_count > 0,
            )
        )
        .order_by(KnowledgeState.next_review)
        .limit(5)
    )
    due_reviews = due_reviews_result.all()

    tasks: list[DailyTaskItem] = []
    for ks, kp in due_reviews:
        completed = ks.knowledge_point_id in completed_kp_ids
        tasks.append(DailyTaskItem(
            id=f"review-{kp.id}",
            title=f"复习: {kp.name}",
            type="review",
            xp=20,
            completed=completed,
            knowledge_point_id=kp.id,
        ))

    in_progress_result = await db.execute(
        select(KnowledgeState, KnowledgePoint)
        .join(KnowledgePoint, KnowledgeState.knowledge_point_id == KnowledgePoint.id)
        .where(
            and_(
                KnowledgeState.student_id == student_id,
                KnowledgeState.mastery_level.in_(["learning", "reviewing"]),
                KnowledgeState.knowledge_point_id.notin_(completed_kp_ids),
            )
        )
        .order_by(KnowledgeState.mastery.desc())
        .limit(3)
    )
    in_progress = in_progress_result.all()

    kp_ids = [kp.id for ks, kp in in_progress]
    if kp_ids:
        lesson_result = await db.execute(
            select(Lesson.knowledge_point_id, Lesson.id).where(
                Lesson.knowledge_point_id.in_(kp_ids)
            )
        )
        lesson_map = dict(lesson_result.all())
    else:
        lesson_map = {}

    for ks, kp in in_progress:
        lesson_id = lesson_map.get(kp.id)

        tasks.append(DailyTaskItem(
            id=f"lesson-{kp.id}",
            title=f"继续学习: {kp.name}",
            type="lesson",
            xp=50,
            completed=False,
            knowledge_point_id=kp.id,
            lesson_id=lesson_id,
        ))

    weak_result = await db.execute(
        select(KnowledgeState, KnowledgePoint)
        .join(KnowledgePoint, KnowledgeState.knowledge_point_id == KnowledgePoint.id)
        .where(
            and_(
                KnowledgeState.student_id == student_id,
                KnowledgeState.mastery < 0.5,
                KnowledgeState.attempts > 0,
                KnowledgeState.knowledge_point_id.notin_(completed_kp_ids),
            )
        )
        .order_by(KnowledgeState.mastery)
        .limit(2)
    )
    weak_kps = weak_result.all()

    for ks, kp in weak_kps:
        tasks.append(DailyTaskItem(
            id=f"practice-{kp.id}",
            title=f"练习: {kp.name}",
            type="practice",
            xp=30,
            completed=False,
            knowledge_point_id=kp.id,
        ))

    completed_count = sum(1 for t in tasks if t.completed)
    total_xp = sum(t.xp for t in tasks if not t.completed)

    return DailyTasksResponse(
        tasks=tasks,
        total_xp_available=total_xp,
        completed_count=completed_count,
    )


async def _get_mastery_summary(db, student_id: UUID) -> MasterySummaryResponse:
    result = await db.execute(
        select(
            KnowledgePoint.pillar,
            func.avg(KnowledgeState.mastery),
        )
        .join(KnowledgeState, KnowledgeState.knowledge_point_id == KnowledgePoint.id)
        .where(
            and_(
                KnowledgeState.student_id == student_id,
                KnowledgePoint.pillar.isnot(None),
            )
        )
        .group_by(KnowledgePoint.pillar)
    )

    subjects = []
    total_mastery = 0.0
    for pillar, avg_mastery in result.all():
        if pillar is None or avg_mastery is None:
            continue
        m = round(float(avg_mastery), 4)
        subjects.append(PillarMastery(
            name=pillar,
            mastery=m,
            color=PILLAR_COLORS.get(pillar, DEFAULT_COLOR),
        ))
        total_mastery += m

    overall = round(total_mastery / len(subjects), 4) if subjects else 0.0

    return MasterySummaryResponse(
        subjects=subjects,
        overall_mastery=overall,
    )


async def _get_streak(db, student_id: UUID) -> StreakResponse:
    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student_id)
    )
    profile = profile_result.scalar_one_or_none()

    current_streak = profile.streak_days if profile else 0
    longest_streak = profile.longest_streak if profile else 0
    total_xp = profile.xp_total if profile else 0
    daily_goal_minutes = profile.daily_goal_minutes if profile else 20

    week_start_dt, week_end_dt = _week_range()
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    week_data = [False] * 7
    for i in range(7):
        d = monday + timedelta(days=i)
        if d > today:
            break
        d_start = datetime.combine(d, datetime.min.time())
        d_end = datetime.combine(d + timedelta(days=1), datetime.min.time())

        session_result = await db.execute(
            select(func.sum(LearningSession.duration_sec)).where(
                and_(
                    LearningSession.student_id == student_id,
                    LearningSession.started_at >= d_start,
                    LearningSession.started_at < d_end,
                )
            )
        )
        total_sec = session_result.scalar() or 0
        week_data[i] = (total_sec / 60.0) >= (daily_goal_minutes * 0.5)

    return StreakResponse(
        current_streak=current_streak,
        longest_streak=longest_streak,
        week_data=week_data,
        total_xp=total_xp,
        daily_goal_minutes=daily_goal_minutes,
    )


@router.get("/daily-tasks", response_model=DailyTasksResponse)
async def get_daily_tasks(
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    return await _get_daily_tasks(db, current_user.id)


@router.get("/mastery-summary", response_model=MasterySummaryResponse)
async def get_mastery_summary(
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    return await _get_mastery_summary(db, current_user.id)


@router.get("/streak", response_model=StreakResponse)
async def get_streak(
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    return await _get_streak(db, current_user.id)


@router.get("/summary", response_model=DashboardSummaryResponse)
async def get_dashboard_summary(
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    daily_tasks = await _get_daily_tasks(db, current_user.id)
    mastery_summary = await _get_mastery_summary(db, current_user.id)
    streak = await _get_streak(db, current_user.id)

    return DashboardSummaryResponse(
        daily_tasks=daily_tasks,
        mastery_summary=mastery_summary,
        streak=streak,
    )
