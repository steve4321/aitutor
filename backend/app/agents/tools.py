"""DB query functions for LangGraph agents."""
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning import KnowledgeState
from app.models.knowledge import KnowledgePoint
from app.models.problem import Problem, ProblemSolution
from app.models.message import Message
from app.models.user import User, StudentProfile
from app.models.course import Lesson


async def load_student_context(db: AsyncSession, student_id: UUID) -> dict:
    """Load student profile + knowledge states."""
    result = await db.execute(
        select(User, StudentProfile)
        .join(StudentProfile, StudentProfile.user_id == User.id)
        .where(User.id == student_id)
    )
    row = result.first()
    if not row:
        return {"student_id": student_id}

    user, profile = row

    # Load knowledge states with KP info
    kp_result = await db.execute(
        select(KnowledgeState, KnowledgePoint)
        .join(KnowledgePoint, KnowledgePoint.id == KnowledgeState.knowledge_point_id)
        .where(KnowledgeState.student_id == student_id)
    )
    kp_rows = kp_result.all()

    mastered = [kp.code for ks, kp in kp_rows if ks.mastery >= 0.85]
    weak = list({kp.pillar for ks, kp in kp_rows if kp.pillar and ks.mastery < 0.4})

    return {
        "student_id": student_id,
        "name": user.name,
        "grade_level": profile.grade_level,
        "target_exam": profile.target_exam,
        "preferred_lang": profile.preferred_lang,
        "diagnostic_done": profile.diagnostic_done,
        "mastered_kps": mastered,
        "weak_areas": weak,
    }


async def load_session_messages(
    db: AsyncSession, session_id: UUID, limit: int = 20
) -> list[dict]:
    """Load recent messages for context window."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(reversed(result.scalars().all()))
    return [{"role": m.role, "content": m.content} for m in messages]


async def load_knowledge_states(
    db: AsyncSession, student_id: UUID
) -> list[dict]:
    """Load all knowledge states for student."""
    result = await db.execute(
        select(KnowledgeState).where(KnowledgeState.student_id == student_id)
    )
    states = result.scalars().all()
    return [
        {
            "knowledge_point_id": str(ks.knowledge_point_id),
            "mastery": ks.mastery,
            "mastery_level": ks.mastery_level,
            "difficulty": ks.difficulty,
            "stability": ks.stability,
            "retrievability": ks.retrievability,
            "next_review": ks.next_review.isoformat() if ks.next_review else None,
            "review_count": ks.review_count,
        }
        for ks in states
    ]


async def load_problem(db: AsyncSession, problem_id: UUID) -> dict | None:
    """Load problem with solutions."""
    result = await db.execute(select(Problem).where(Problem.id == problem_id))
    problem = result.scalar_one_or_none()
    if not problem:
        return None

    data = {
        "id": str(problem.id),
        "subject": problem.subject,
        "format": problem.format,
        "question_markdown": problem.question_markdown,
        "options": problem.options,
        "correct_answer": problem.correct_answer,
        "difficulty": problem.difficulty,
        "hints": problem.hints,
        "misconceptions": problem.misconceptions,
        "step_decomposition": problem.step_decomposition,
        "knowledge_point_ids": problem.knowledge_point_ids,
    }

    sol_result = await db.execute(
        select(ProblemSolution)
        .where(ProblemSolution.problem_id == problem_id)
        .order_by(ProblemSolution.sort_order)
    )
    solutions = sol_result.scalars().all()
    data["solutions"] = [
        {
            "method_name": s.method_name,
            "solution_markdown": s.solution_markdown,
            "key_insight": s.key_insight,
        }
        for s in solutions
    ]

    return data


async def load_lesson(db: AsyncSession, lesson_id: UUID) -> dict | None:
    """Load lesson data."""
    result = await db.execute(select(Lesson).where(Lesson.id == lesson_id))
    lesson = result.scalar_one_or_none()
    if not lesson:
        return None
    return {
        "id": str(lesson.id),
        "title": lesson.title,
        "lesson_type": lesson.lesson_type,
        "content": lesson.content,
        "knowledge_point_id": str(lesson.knowledge_point_id) if lesson.knowledge_point_id else None,
        "estimated_minutes": lesson.estimated_minutes,
    }
