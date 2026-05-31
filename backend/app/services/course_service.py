from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course, Unit, Lesson


async def get_courses(db: AsyncSession, subject: str | None = None) -> list[Course]:
    stmt = select(Course)
    if subject:
        stmt = stmt.where(Course.subject == subject)
    stmt = stmt.order_by(Course.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_course_detail(db: AsyncSession, course_id) -> Course | None:
    stmt = select(Course).where(Course.id == course_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def get_course_units(db: AsyncSession, course_id) -> list[Unit]:
    stmt = select(Unit).where(Unit.course_id == course_id).order_by(Unit.sort_order)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_course_lessons(db: AsyncSession, course_id) -> list[Lesson]:
    stmt = (
        select(Lesson)
        .join(Unit, Lesson.unit_id == Unit.id)
        .where(Unit.course_id == course_id)
        .order_by(Unit.sort_order, Lesson.sort_order)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())