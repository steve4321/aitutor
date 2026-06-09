import pytest

from app.models.course import Course, Lesson, Unit
from app.services.course_service import (
    get_course_detail,
    get_course_lessons,
    get_course_units,
    get_courses,
)


@pytest.mark.asyncio
async def test_get_courses_returns_all_when_no_filter(db_session):
    c1 = Course(code="C1", subject="math", name="Beta Course")
    c2 = Course(code="C2", subject="english", name="Alpha Course")
    db_session.add_all([c1, c2])
    await db_session.flush()

    courses = await get_courses(db_session)
    assert len(courses) == 2
    names = [c.name for c in courses]
    assert "Beta Course" in names
    assert "Alpha Course" in names


@pytest.mark.asyncio
async def test_get_courses_orders_by_name(db_session):
    c1 = Course(code="C3", subject="math", name="Zebra")
    c2 = Course(code="C4", subject="math", name="Apple")
    c3 = Course(code="C5", subject="math", name="Mango")
    db_session.add_all([c1, c2, c3])
    await db_session.flush()

    courses = await get_courses(db_session)
    assert [c.name for c in courses] == ["Apple", "Mango", "Zebra"]


@pytest.mark.asyncio
async def test_get_courses_filters_by_subject(db_session):
    c1 = Course(code="C6", subject="math", name="Math1")
    c2 = Course(code="C7", subject="english", name="Eng1")
    db_session.add_all([c1, c2])
    await db_session.flush()

    courses = await get_courses(db_session, subject="math")
    assert len(courses) == 1
    assert courses[0].subject == "math"
    assert courses[0].name == "Math1"


@pytest.mark.asyncio
async def test_get_courses_empty_list_when_no_courses(db_session):
    courses = await get_courses(db_session)
    assert courses == []


@pytest.mark.asyncio
async def test_get_course_detail_valid_id(db_session, published_course):
    course = await get_course_detail(db_session, published_course["course_id"])
    assert course is not None
    assert course.id == published_course["course_id"]
    assert course.name == "测试课程"


@pytest.mark.asyncio
async def test_get_course_detail_nonexistent_id(db_session):
    from uuid import uuid4

    course = await get_course_detail(db_session, uuid4())
    assert course is None


@pytest.mark.asyncio
async def test_get_course_units_ordered_by_sort_order(db_session, published_course):
    course_id = published_course["course_id"]
    unit2 = Unit(course_id=course_id, name="第三章", sort_order=3)
    unit0 = Unit(course_id=course_id, name="第零章", sort_order=0)
    db_session.add_all([unit2, unit0])
    await db_session.flush()

    units = await get_course_units(db_session, course_id)
    assert len(units) == 3
    assert units[0].sort_order == 0
    assert units[1].sort_order == 1
    assert units[2].sort_order == 3


@pytest.mark.asyncio
async def test_get_course_units_empty_when_no_units(db_session):
    c = Course(code="NO-UNITS", subject="math", name="Empty")
    db_session.add(c)
    await db_session.flush()

    units = await get_course_units(db_session, c.id)
    assert units == []


@pytest.mark.asyncio
async def test_get_course_lessons_ordered_by_unit_and_lesson_sort(db_session, published_course):
    course_id = published_course["course_id"]

    result = await db_session.execute(
        Unit.__table__.select().where(Unit.course_id == course_id)
    )
    existing_unit_id = result.fetchall()[0][0]

    unit2 = Unit(course_id=course_id, name="第二单元", sort_order=2)
    db_session.add(unit2)
    await db_session.flush()

    lesson_b = Lesson(
        unit_id=existing_unit_id,
        title="Lesson B",
        lesson_type="concept",
        content={"steps": []},
        estimated_minutes=10,
        sort_order=2,
    )
    lesson_a = Lesson(
        unit_id=existing_unit_id,
        title="Lesson A",
        lesson_type="concept",
        content={"steps": []},
        estimated_minutes=10,
        sort_order=1,
    )
    lesson_c = Lesson(
        unit_id=unit2.id,
        title="Lesson C",
        lesson_type="practice",
        content={"steps": []},
        estimated_minutes=15,
        sort_order=1,
    )
    db_session.add_all([lesson_b, lesson_a, lesson_c])
    await db_session.flush()

    lessons = await get_course_lessons(db_session, course_id)
    assert len(lessons) == 4
    assert lessons[0].sort_order <= lessons[1].sort_order


@pytest.mark.asyncio
async def test_get_course_lessons_empty_when_no_lessons(db_session):
    c = Course(code="NO-LESSONS", subject="math", name="Empty Lessons")
    db_session.add(c)
    await db_session.flush()

    lessons = await get_course_lessons(db_session, c.id)
    assert lessons == []
