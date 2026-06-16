import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement

logger = logging.getLogger(__name__)

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


async def check_and_award(
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
