"""Seed the database with curriculum data for development.

Usage: cd backend && python -m scripts.seed_data
"""
import asyncio
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Add parent dir to path so imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.core.security import hash_password
from app.models import (
    Base,
    Course,
    KnowledgeDependency,
    KnowledgePoint,
    LearningSession,
    Lesson,
    Problem,
    StudentProfile,
    Unit,
    User,
)
from scripts.curriculum_amc import (
    AMC_COURSES,
    AMC_KNOWLEDGE_DEPENDENCIES,
    AMC_KNOWLEDGE_POINTS,
    AMC_PROBLEMS,
)
from scripts.curriculum_chinese import (
    CHINESE_COURSES,
    CHINESE_KNOWLEDGE_DEPENDENCIES,
    CHINESE_KNOWLEDGE_POINTS,
    CHINESE_PROBLEMS,
)
from scripts.curriculum_ket import (
    KET_COURSE,
    KET_KNOWLEDGE_DEPENDENCIES,
    KET_KNOWLEDGE_POINTS,
    KET_PROBLEMS,
)


async def seed():
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as db:
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("Database already has data. Skipping seed.")
            await engine.dispose()
            return

        student = User(
            name="teststudent",
            email="student@test.com",
            password_hash=hash_password("test123"),
            role="student",
        )
        db.add(student)
        await db.flush()

        db.add(StudentProfile(
            user_id=student.id,
            grade_level=5,
            target_exam="AMC8",
            target_date=date(2026, 11, 15),
            daily_goal_minutes=20,
            diagnostic_done=True,
            xp_total=150,
            streak_days=3,
            longest_streak=7,
        ))

        parent = User(
            name="testparent",
            email="parent@test.com",
            password_hash=hash_password("test123"),
            role="parent",
        )
        db.add(parent)
        await db.flush()

        all_courses_raw = AMC_COURSES + [KET_COURSE] + CHINESE_COURSES

        courses: list[Course] = []
        for cr in all_courses_raw:
            course_obj = Course(
                code=cr["code"],
                subject=cr["subject"],
                name=cr["name"],
                description=cr["description"],
                target_exam=cr.get("target_exam"),
                estimated_hours=cr["estimated_hours"],
                is_published=cr["is_published"],
            )
            db.add(course_obj)
            courses.append(course_obj)
        await db.flush()

        all_kp_data = AMC_KNOWLEDGE_POINTS + KET_KNOWLEDGE_POINTS + CHINESE_KNOWLEDGE_POINTS
        kp_objects: list[KnowledgePoint] = []
        for kp_data in all_kp_data:
            kp_obj = KnowledgePoint(**kp_data)
            db.add(kp_obj)
            kp_objects.append(kp_obj)
        await db.flush()

        kp_code_to_id = {kp.code: kp.id for kp in kp_objects}
        kp_code_to_obj = {kp.code: kp for kp in kp_objects}

        unit_objects: list[Unit] = []
        lesson_objects: list[Lesson] = []

        for course_obj, cr in zip(courses, all_courses_raw):
            for unit_d in cr["units"]:
                unit_obj = Unit(
                    course_id=course_obj.id,
                    code=unit_d["code"],
                    name=unit_d["name"],
                    description=unit_d["description"],
                    sort_order=unit_d["sort_order"],
                    required_mastery=unit_d["required_mastery"],
                )
                db.add(unit_obj)
                unit_objects.append((unit_obj, unit_d))
        await db.flush()

        for unit_obj, unit_d in unit_objects:
            for ld in unit_d["lessons"]:
                kp_code = ld.get("knowledge_point_code")
                lesson_obj = Lesson(
                    unit_id=unit_obj.id,
                    code=ld["code"],
                    title=ld["title"],
                    lesson_type=ld["lesson_type"],
                    content=ld["content"],
                    estimated_minutes=ld["estimated_minutes"],
                    sort_order=ld["sort_order"],
                    is_published=ld["is_published"],
                    knowledge_point_id=kp_code_to_id.get(kp_code) if kp_code else None,
                )
                db.add(lesson_obj)
                lesson_objects.append(lesson_obj)

                if kp_code and kp_code in kp_code_to_obj:
                    kp_code_to_obj[kp_code].lesson_id = lesson_obj.id

        await db.flush()

        unit_objects_list = [uo for uo, _ in unit_objects]

        all_dep_data = (
            AMC_KNOWLEDGE_DEPENDENCIES
            + KET_KNOWLEDGE_DEPENDENCIES
            + CHINESE_KNOWLEDGE_DEPENDENCIES
        )
        dep_count = 0
        for dep in all_dep_data:
            if isinstance(dep, dict):
                prereq_code, target_code = dep["prerequisite_code"], dep["target_code"]
            else:
                prereq_code, target_code = dep[0], dep[1]

            prereq_id = kp_code_to_id.get(prereq_code)
            target_id = kp_code_to_id.get(target_code)
            if prereq_id and target_id:
                db.add(KnowledgeDependency(
                    prerequisite_id=prereq_id,
                    target_id=target_id,
                    dependency_type="prerequisite",
                    strength=1,
                ))
                dep_count += 1
        await db.flush()

        all_problem_data = AMC_PROBLEMS + KET_PROBLEMS + CHINESE_PROBLEMS
        problem_count = 0
        for prob_data in all_problem_data:
            kp_codes = prob_data.pop("knowledge_point_codes")
            kp_ids = [str(kp_code_to_id[c]) for c in kp_codes if c in kp_code_to_id]
            if not kp_ids:
                continue
            db.add(Problem(
                knowledge_point_ids=kp_ids,
                times_attempted=0,
                times_correct=0,
                **prob_data,
            ))
            problem_count += 1
        await db.flush()

        now = datetime.now(timezone.utc)
        sample_kp_ids = list(kp_code_to_id.values())[:2]
        sessions_data = []
        if len(sample_kp_ids) >= 2:
            sessions_data = [
                {
                    "student_id": student.id,
                    "session_type": "practice",
                    "subject": "math",
                    "knowledge_point_id": sample_kp_ids[0],
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
                    "knowledge_point_id": sample_kp_ids[1],
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
            db.add(LearningSession(**s))

        await db.commit()

        try:
            from app.services.embedding_service import (
                backfill_problem_embeddings,
                backfill_knowledge_point_embeddings,
            )
            pc = await backfill_problem_embeddings(db)
            kc = await backfill_knowledge_point_embeddings(db)
            print(f"  Embeddings backfilled: {pc} problems, {kc} knowledge points")
        except Exception:
            print("  Embedding backfill skipped (no API key or model unavailable)")

        print("=" * 60)
        print("Seed data created successfully!")
        print("=" * 60)
        print("  Users: teststudent (student), testparent (parent), password: test123")
        print(f"  Courses: {len(courses)}")
        print(f"  Units: {len(unit_objects_list)}")
        print(f"  Lessons: {len(lesson_objects)}")
        print(f"  Knowledge Points: {len(kp_objects)}")
        print(f"  Problems: {problem_count}")
        print(f"  Dependencies: {dep_count}")
        print(f"  Learning Sessions: {len(sessions_data)}")
        print("=" * 60)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
