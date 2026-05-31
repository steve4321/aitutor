"""Seed the database with sample data for development.

Usage: cd backend && python -m scripts.seed_data
"""
import asyncio
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Add parent dir to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.security import hash_password
from app.models import (
    Base,
    Course,
    KnowledgePoint,
    LearningSession,
    Lesson,
    Problem,
    StudentProfile,
    Unit,
    User,
)


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        # Check if data already exists
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already has data. Skipping seed.")
            await engine.dispose()
            return

        # 1. Create test users
        student = User(
            name="teststudent",
            email="student@test.com",
            password_hash=hash_password("test123"),
            role="student",
        )
        db.add(student)
        await db.flush()

        profile = StudentProfile(
            user_id=student.id,
            grade_level=5,
            target_exam="AMC8",
            target_date=date(2026, 11, 15),
            daily_goal_minutes=20,
            diagnostic_done=True,
            xp_total=150,
            streak_days=3,
            longest_streak=7,
        )
        db.add(profile)

        parent = User(
            name="testparent",
            email="parent@test.com",
            password_hash=hash_password("test123"),
            role="parent",
        )
        db.add(parent)
        await db.flush()

        # 2. Create courses (matching course-catalog.md)
        courses_data = [
            {
                "code": "AMC8-A",
                "subject": "math",
                "name": "AMC 8 基础班",
                "description": "AMC 8 竞赛基础训练",
                "target_exam": "AMC8",
                "estimated_hours": 40,
                "is_published": True,
            },
            {
                "code": "AMC8-B",
                "subject": "math",
                "name": "AMC 8 提高班",
                "description": "AMC 8 竞赛提高训练",
                "target_exam": "AMC8",
                "estimated_hours": 60,
                "is_published": True,
            },
            {
                "code": "KET-A",
                "subject": "english",
                "name": "KET 基础班",
                "description": "KET 考试基础训练",
                "target_exam": "KET",
                "estimated_hours": 30,
                "is_published": True,
            },
            {
                "code": "CN-B5",
                "subject": "chinese",
                "name": "语文·作文五年级",
                "description": "小学五年级作文训练",
                "target_exam": None,
                "estimated_hours": 20,
                "is_published": True,
            },
            {
                "code": "CN-C4",
                "subject": "chinese",
                "name": "语文·古诗词四年级",
                "description": "小学四年级古诗词赏析",
                "target_exam": None,
                "estimated_hours": 15,
                "is_published": True,
            },
        ]

        courses = []
        for c in courses_data:
            course = Course(**c)
            db.add(course)
            courses.append(course)
        await db.flush()

        # 3. Create units for AMC8-A
        units_data = [
            {
                "course_id": courses[0].id,
                "code": "AMC8-A-U1",
                "name": "算术与数论",
                "sort_order": 1,
                "required_mastery": 0.8,
            },
            {
                "course_id": courses[0].id,
                "code": "AMC8-A-U2",
                "name": "代数基础",
                "sort_order": 2,
                "required_mastery": 0.8,
            },
            {
                "course_id": courses[0].id,
                "code": "AMC8-A-U3",
                "name": "几何入门",
                "sort_order": 3,
                "required_mastery": 0.8,
            },
            {
                "course_id": courses[0].id,
                "code": "AMC8-A-U4",
                "name": "计数与概率",
                "sort_order": 4,
                "required_mastery": 0.8,
            },
        ]

        units = []
        for u in units_data:
            unit = Unit(**u)
            db.add(unit)
            units.append(unit)
        await db.flush()

        # 4. Create knowledge points
        kp_data = [
            {
                "code": "math-arith-01",
                "subject": "math",
                "name": "整除与余数",
                "name_en": "Divisibility and Remainders",
                "pillar": "数论",
                "difficulty_level": 2,
                "amc_level": 8,
            },
            {
                "code": "math-alg-01",
                "subject": "math",
                "name": "一元一次方程",
                "name_en": "Linear Equations",
                "pillar": "代数",
                "difficulty_level": 2,
                "amc_level": 8,
            },
            {
                "code": "math-geo-01",
                "subject": "math",
                "name": "三角形面积",
                "name_en": "Triangle Area",
                "pillar": "几何",
                "difficulty_level": 2,
                "amc_level": 8,
            },
            {
                "code": "math-count-01",
                "subject": "math",
                "name": "排列组合基础",
                "name_en": "Permutations and Combinations",
                "pillar": "组合",
                "difficulty_level": 3,
                "amc_level": 8,
            },
        ]

        kps = []
        for kp in kp_data:
            point = KnowledgePoint(**kp)
            db.add(point)
            kps.append(point)
        await db.flush()

        # 5. Create lessons for each unit
        lessons_data = [
            {
                "unit_id": units[0].id,
                "knowledge_point_id": kps[0].id,
                "code": "AMC8-A-L01",
                "title": "整除性判定",
                "lesson_type": "practice",
                "content": {
                    "blocks": [{"type": "text", "content": "学习整除性判定法则"}],
                    "steps": [],
                },
                "estimated_minutes": 20,
                "sort_order": 1,
                "is_published": True,
            },
            {
                "unit_id": units[0].id,
                "knowledge_point_id": kps[0].id,
                "code": "AMC8-A-L02",
                "title": "余数问题",
                "lesson_type": "practice",
                "content": {
                    "blocks": [{"type": "text", "content": "学习余数运算技巧"}],
                    "steps": [],
                },
                "estimated_minutes": 25,
                "sort_order": 2,
                "is_published": True,
            },
            {
                "unit_id": units[1].id,
                "knowledge_point_id": kps[1].id,
                "code": "AMC8-A-L03",
                "title": "方程求解",
                "lesson_type": "practice",
                "content": {
                    "blocks": [{"type": "text", "content": "一元一次方程的解法"}],
                    "steps": [],
                },
                "estimated_minutes": 20,
                "sort_order": 1,
                "is_published": True,
            },
            {
                "unit_id": units[2].id,
                "knowledge_point_id": kps[2].id,
                "code": "AMC8-A-L04",
                "title": "三角形面积计算",
                "lesson_type": "practice",
                "content": {
                    "blocks": [{"type": "text", "content": "三角形面积公式及应用"}],
                    "steps": [],
                },
                "estimated_minutes": 15,
                "sort_order": 1,
                "is_published": True,
            },
            {
                "unit_id": units[3].id,
                "knowledge_point_id": kps[3].id,
                "code": "AMC8-A-L05",
                "title": "排列与组合",
                "lesson_type": "practice",
                "content": {
                    "blocks": [{"type": "text", "content": "排列组合的基本概念"}],
                    "steps": [],
                },
                "estimated_minutes": 30,
                "sort_order": 1,
                "is_published": True,
            },
        ]

        for l in lessons_data:
            lesson = Lesson(**l)
            db.add(lesson)
        await db.flush()

        # 6. Create sample problems (AMC 8 style)
        problems_data = [
            {
                "source": "AMC8",
                "source_year": 2024,
                "source_code": "AMC8-2024-01",
                "subject": "math",
                "format": "mcq",
                "question_markdown": "## Problem 1\n\nWhat is the value of $2 + 2 \\times 3$?",
                "options": {"A": "8", "B": "12", "C": "10", "D": "6"},
                "correct_answer": "A",
                "difficulty": 1,
                "estimated_time_sec": 60,
                "knowledge_point_ids": [str(kps[0].id)],
            },
            {
                "source": "AMC8",
                "source_year": 2024,
                "source_code": "AMC8-2024-02",
                "subject": "math",
                "format": "mcq",
                "question_markdown": "## Problem 2\n\nA rectangle has a length of 8 and a width of 5. What is its perimeter?",
                "options": {"A": "13", "B": "26", "C": "40", "D": "30"},
                "correct_answer": "B",
                "difficulty": 1,
                "estimated_time_sec": 45,
                "knowledge_point_ids": [str(kps[2].id)],
            },
            {
                "source": "AMC8",
                "source_year": 2024,
                "source_code": "AMC8-2024-03",
                "subject": "math",
                "format": "mcq",
                "question_markdown": "## Problem 3\n\nHow many positive integers less than 100 are divisible by both 3 and 5?",
                "options": {"A": "5", "B": "6", "C": "7", "D": "8"},
                "correct_answer": "B",
                "difficulty": 2,
                "estimated_time_sec": 120,
                "knowledge_point_ids": [str(kps[0].id)],
            },
            {
                "source": "AMC8",
                "source_year": 2024,
                "source_code": "AMC8-2024-04",
                "subject": "math",
                "format": "mcq",
                "question_markdown": "## Problem 4\n\nIf $3x + 7 = 22$, what is $x$?",
                "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
                "correct_answer": "C",
                "difficulty": 1,
                "estimated_time_sec": 60,
                "knowledge_point_ids": [str(kps[1].id)],
            },
            {
                "source": "AMC8",
                "source_year": 2024,
                "source_code": "AMC8-2024-05",
                "subject": "math",
                "format": "mcq",
                "question_markdown": "## Problem 5\n\nIn how many ways can 3 students be arranged in a line?",
                "options": {"A": "3", "B": "6", "C": "9", "D": "12"},
                "correct_answer": "B",
                "difficulty": 2,
                "estimated_time_sec": 90,
                "knowledge_point_ids": [str(kps[3].id)],
            },
        ]

        for p in problems_data:
            problem = Problem(**p)
            db.add(problem)
        await db.flush()

        # 7. Create sample learning sessions (recent ones for report testing)
        now = datetime.now(timezone.utc)
        sessions_data = [
            {
                "student_id": student.id,
                "session_type": "practice",
                "subject": "math",
                "knowledge_point_id": kps[0].id,
                "started_at": now - timedelta(hours=2),
                "ended_at": now - timedelta(hours=2, minutes=-25),
                "duration_sec": 1500,
                "problems_total": 5,
                "problems_correct": 4,
                "score_pct": 80.0,
                "xp_earned": 40,
                "summary": "练习了整除与余数，正确率80%",
            },
            {
                "student_id": student.id,
                "session_type": "practice",
                "subject": "math",
                "knowledge_point_id": kps[1].id,
                "started_at": now - timedelta(days=1),
                "ended_at": now - timedelta(days=1, minutes=-20),
                "duration_sec": 1200,
                "problems_total": 4,
                "problems_correct": 3,
                "score_pct": 75.0,
                "xp_earned": 30,
                "summary": "方程求解练习",
            },
        ]

        for s in sessions_data:
            session = LearningSession(**s)
            db.add(session)

        await db.commit()
        print("✅ Seed data created successfully!")
        print(
            f"  Users: teststudent (student), testparent (parent), password: test123"
        )
        print(
            f"  Courses: {len(courses)} ({', '.join(c.code for c in courses)})"
        )
        print(f"  Units: {len(units)}")
        print(f"  Lessons: {len(lessons_data)}")
        print(f"  Knowledge Points: {len(kps)}")
        print(f"  Problems: {len(problems_data)}")
        print(f"  Learning Sessions: {len(sessions_data)}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
