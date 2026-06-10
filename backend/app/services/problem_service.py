from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problem import Problem
from app.agents.evaluation_helpers import heuristic_evaluate


async def get_problem(db: AsyncSession, problem_id: UUID) -> Problem | None:
    stmt = select(Problem).where(Problem.id == problem_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_problems(
    db: AsyncSession,
    subject: str | None = None,
    knowledge_point_id: UUID | None = None,
    difficulty: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> list[Problem]:
    stmt = select(Problem)
    if subject:
        stmt = stmt.where(Problem.subject == subject)
    if knowledge_point_id:
        stmt = stmt.where(
            Problem.knowledge_point_ids.contains([str(knowledge_point_id)])
        )
    if difficulty:
        stmt = stmt.where(Problem.difficulty == difficulty)
    stmt = stmt.order_by(Problem.difficulty).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def evaluate_attempt(db: AsyncSession, problem_id: UUID, answer: str) -> dict | None:
    """Evaluate a student's answer against the correct answer."""
    problem = await get_problem(db, problem_id)
    if not problem:
        return None

    is_correct = False
    ai_feedback = ""

    if problem.format == "mcq" and problem.correct_answer:
        is_correct = (answer.strip().upper() == problem.correct_answer.strip().upper())
        if is_correct:
            ai_feedback = "Correct! Well done."
        else:
            ai_feedback = f"Not quite. The correct answer is {problem.correct_answer}."
    else:
        result = heuristic_evaluate(
            answer=answer,
            correct_answer=problem.correct_answer,
            problem_format=problem.format,
        )
        is_correct = result["is_correct"]
        ai_feedback = result["feedback"]

    return {
        "is_correct": is_correct,
        "ai_feedback": ai_feedback,
        "attempt_number": 1,
    }