"""Unified gamification orchestration.

Combines XP awarding, streak tracking, and achievement checking into a single
coherent flow.  Both :mod:`xp_service` and :mod:`achievement_service` delegate
here so that neither ever imports the other, eliminating the circular-import
risk that existed when ``xp_service`` imported ``achievement_service`` at call
time.

Dependency direction (acyclic)::

    xp_service ──────────┐
                         ├──▶ gamification_service ──▶ models
    achievement_service ─┘
"""
import logging
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement

logger = logging.getLogger(__name__)

LESSON_XP_REWARD = 50
PROBLEM_XP_REWARD = 20

ACHIEVEMENT_DEFS = [
    {
        "code": "first_lesson",
        "title": "第一课",
        "description": "完成第一节课",
        "condition": lambda stats: stats["lessons_completed"] >= 1,
    },
    {
        "code": "first_problem",
        "title": "初试身手",
        "description": "答对第一道题",
        "condition": lambda stats: stats["problems_correct"] >= 1,
    },
    {
        "code": "streak_7",
        "title": "坚持一周",
        "description": "连续学习7天",
        "condition": lambda stats: stats["streak_days"] >= 7,
    },
    {
        "code": "streak_30",
        "title": "月度坚持",
        "description": "连续学习30天",
        "condition": lambda stats: stats["streak_days"] >= 30,
    },
    {
        "code": "xp_100",
        "title": "百分达人",
        "description": "累计获得100 XP",
        "condition": lambda stats: stats["xp_total"] >= 100,
    },
    {
        "code": "xp_500",
        "title": "积分高手",
        "description": "累计获得500 XP",
        "condition": lambda stats: stats["xp_total"] >= 500,
    },
    {
        "code": "xp_1000",
        "title": "千分大师",
        "description": "累计获得1000 XP",
        "condition": lambda stats: stats["xp_total"] >= 1000,
    },
    {
        "code": "problems_50",
        "title": "刷题达人",
        "description": "答对50道题",
        "condition": lambda stats: stats["problems_correct"] >= 50,
    },
]


async def update_streak(
    db: AsyncSession,
    user_id: UUID,
    profile=None,
) -> int:
    from app.models.user import StudentProfile

    if profile is None:
        result = await db.execute(
            select(StudentProfile).where(StudentProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
    if profile is None:
        return 0

    today = date.today()
    if profile.last_active_date == today:
        return profile.streak_days

    if profile.last_active_date == today - timedelta(days=1):
        profile.streak_days = (profile.streak_days or 0) + 1
    else:
        profile.streak_days = 1

    profile.longest_streak = max(profile.longest_streak or 0, profile.streak_days)
    profile.last_active_date = today
    return profile.streak_days


async def build_achievement_stats(
    db: AsyncSession, user_id: UUID, profile
) -> dict:
    from app.models.learning import LearningSession, StudentAttempt

    lessons_result = await db.execute(
        select(func.count()).select_from(LearningSession).where(
            LearningSession.student_id == user_id,
            LearningSession.session_type == "lesson",
            LearningSession.ended_at.isnot(None),
        )
    )
    lessons_completed = lessons_result.scalar() or 0

    problems_result = await db.execute(
        select(func.count()).select_from(StudentAttempt).where(
            StudentAttempt.student_id == user_id,
            StudentAttempt.is_correct.is_(True),
        )
    )
    problems_correct = problems_result.scalar() or 0

    return {
        "lessons_completed": lessons_completed,
        "problems_correct": problems_correct,
        "streak_days": profile.streak_days or 0,
        "xp_total": profile.xp_total or 0,
    }


async def award_achievements(
    db: AsyncSession, user_id: UUID, stats: dict
) -> list[Achievement]:
    result = await db.execute(
        select(Achievement.code).where(Achievement.student_id == user_id)
    )
    earned_codes = {row[0] for row in result.all()}

    newly_awarded: list[Achievement] = []
    for defn in ACHIEVEMENT_DEFS:
        code = defn["code"]
        if code in earned_codes:
            continue
        try:
            if defn["condition"](stats):
                achievement = Achievement(
                    student_id=user_id,
                    code=code,
                    title=defn["title"],
                    description=defn["description"],
                )
                db.add(achievement)
                newly_awarded.append(achievement)
        except Exception:
            logger.warning(
                "Failed to evaluate achievement %s", code, exc_info=True
            )

    if newly_awarded:
        await db.flush()
    return newly_awarded


async def process_student_progress(
    db: AsyncSession,
    student_id: UUID,
    xp_amount: int,
    context: dict | None = None,
) -> dict:
    """Award XP and check/award achievements in one operation.

    Returns dict with:
    - xp_awarded: int
    - new_achievements: list[Achievement]
    - leveled_up: bool
    """
    from app.models.user import StudentProfile

    result: dict = {
        "xp_awarded": 0,
        "new_achievements": [],
        "leveled_up": False,
    }

    if xp_amount <= 0:
        return result

    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student_id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile is None:
        return result

    profile.xp_total = (profile.xp_total or 0) + xp_amount
    await update_streak(db, student_id, profile=profile)

    try:
        stats = await build_achievement_stats(db, student_id, profile)
        new_achievements = await award_achievements(db, student_id, stats)
    except Exception:
        logger.warning("Achievement check failed", exc_info=True)
        new_achievements = []

    result["xp_awarded"] = xp_amount
    result["new_achievements"] = new_achievements
    return result
