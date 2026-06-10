"""Shared test fixtures: in-memory SQLite DB, seed data, auth helpers, mock LLM."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.models.base import Base
from app.models.user import User, StudentProfile
from app.models.problem import Problem
from app.models.knowledge import KnowledgePoint
from app.models.course import Course, Unit, Lesson
from app.db.session import get_db
from app.core.security import hash_password, create_access_token


# ---------------------------------------------------------------------------
# Engine & DB session
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def engine():
    """Create an in-memory SQLite engine with all tables."""
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def db_session(engine):
    """Provide an auto-rollback async session."""
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    """Async test client wired to the test DB via dependency override."""
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ---------------------------------------------------------------------------
# Seed data fixtures
# ---------------------------------------------------------------------------


@pytest_asyncio.fixture
async def student(db_session):
    """Create a student user with profile."""
    user = User(
        name="测试小明",
        role="student",
        password_hash=hash_password("test123"),
    )
    db_session.add(user)
    await db_session.flush()

    profile = StudentProfile(
        user_id=user.id,
        grade_level=5,
        target_exam="AMC8",
        preferred_lang="zh-CN",
    )
    db_session.add(profile)
    await db_session.flush()
    return user


@pytest_asyncio.fixture
async def knowledge_points(db_session):
    """Create 3 AMC-math knowledge points: algebra, geometry, number theory."""
    kps = [
        KnowledgePoint(
            code="algebra.01",
            subject="amc_math",
            name="一元一次方程",
            name_en="Linear Equations",
        ),
        KnowledgePoint(
            code="geometry.01",
            subject="amc_math",
            name="相似三角形",
            name_en="Similar Triangles",
        ),
        KnowledgePoint(
            code="number.01",
            subject="amc_math",
            name="整除性",
            name_en="Divisibility",
        ),
    ]
    db_session.add_all(kps)
    await db_session.flush()
    return kps


@pytest_asyncio.fixture
async def mcq_problem(db_session, knowledge_points):
    """Create a multiple-choice problem linked to algebra.01."""
    kp = knowledge_points[0]  # algebra.01
    problem = Problem(
        subject="amc_math",
        format="mcq",
        question_markdown="解方程 2x + 3 = 7",
        options={"A": "1", "B": "2", "C": "3", "D": "4"},
        correct_answer="B",
        difficulty=3,
        knowledge_point_ids=[str(kp.id)],
    )
    db_session.add(problem)
    await db_session.flush()
    return problem


@pytest_asyncio.fixture
async def published_course(db_session):
    """Create a published course with one unit and one published lesson with content.

    Returns a dict so tests can access both IDs and the loaded Lesson without
    triggering lazy-load IO in the test body.
    """
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload

    course = Course(
        code="AMC8-TEST",
        subject="math",
        name="测试课程",
        description="测试用",
        target_exam="AMC8",
        is_published=True,
    )
    db_session.add(course)
    await db_session.flush()
    course_id = course.id

    unit = Unit(
        course_id=course_id,
        name="第一章",
        sort_order=1,
    )
    db_session.add(unit)
    await db_session.flush()

    lesson = Lesson(
        unit_id=unit.id,
        title="测试课",
        lesson_type="concept",
        estimated_minutes=20,
        sort_order=1,
        is_published=True,
        content={
            "schema_version": "1.0",
            "subject": "amc_math",
            "lesson_type": "concept",
            "steps": [],
            "objectives": ["目标1", "目标2"],
            "summary": {
                "key_points": ["要点1"],
                "common_mistakes": ["易错1"],
            },
        },
    )
    db_session.add(lesson)
    await db_session.flush()
    lesson_id = lesson.id

    result = await db_session.execute(
        select(Lesson).options(selectinload(Lesson.unit)).where(Lesson.id == lesson_id)
    )
    loaded_lesson = result.scalar_one()

    return {
        "lesson": loaded_lesson,
        "lesson_id": lesson_id,
        "course_id": course_id,
    }


# ---------------------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------------------


@pytest.fixture
def auth_token(student):
    """JWT token for the student user."""
    return create_access_token({"sub": str(student.id)})


@pytest.fixture
def auth_headers(auth_token):
    """Authorization header dict for the student."""
    return {"Authorization": f"Bearer {auth_token}"}


# ---------------------------------------------------------------------------
# Mock LLM utilities
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_llm():
    """AsyncMock LLM that returns an AIMessage with configurable content."""
    from langchain_core.messages import AIMessage

    default_content = "这是AI的回复"
    ai_message = AIMessage(content=default_content)
    mock = AsyncMock(return_value=ai_message)

    with patch("app.agents.llm.get_llm", return_value=mock):
        yield mock


@pytest.fixture
def mock_llm_unavailable():
    """Patch is_llm_available to return False."""
    with patch("app.agents.llm.is_llm_available", return_value=False):
        yield
