"""Shared test fixtures: in-memory SQLite DB, seed data, auth helpers, mock LLM."""
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.models.base import Base
from app.models.user import User, StudentProfile
from app.models.problem import Problem, ProblemSolution
from app.models.knowledge import KnowledgePoint
from app.models.learning import KnowledgeState, LearningSession, StudentAttempt
from app.models.message import Message
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
