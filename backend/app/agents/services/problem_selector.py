"""Adaptive problem selection engine (§8.2 of system-design.md)."""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, not_

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.problem import Problem
from app.models.learning import StudentAttempt


async def select_next_problem(
    db: AsyncSession,
    student_id: UUID,
    subject: str,
    target_exam: str,
    knowledge_states: list[dict],
    session_problem_ids: list[UUID] | None = None,
) -> Problem | None:
    """
    Select the next problem based on adaptive strategy (§8.2).

    Strategy:
    1. Find FSRS-due knowledge points -> select review problems
    2. If no reviews due, find weakest knowledge point (ZPD)
    3. Filter by difficulty +-1 of current mastery
    4. Exclude recently attempted problems (7 days)
    """
    now = datetime.now(timezone.utc)

    due_kp_ids = []
    for ks in knowledge_states:
        next_review = ks.get("next_review")
        if next_review:
            nr = datetime.fromisoformat(next_review) if isinstance(next_review, str) else next_review
            if nr <= now:
                due_kp_ids.append(ks["knowledge_point_id"])

    target_difficulty = 3
    active_kp_ids = []
    if not due_kp_ids:
        active_states = sorted(
            [ks for ks in knowledge_states if 0 < ks["mastery"] < 0.85],
            key=lambda x: x["mastery"],
        )
        if active_states:
            weakest = active_states[0]
            active_kp_ids.append(weakest["knowledge_point_id"])
            target_difficulty = max(1, int(weakest["mastery"] * 10))

    stmt = select(Problem).where(
        Problem.subject == subject,
        Problem.difficulty.isnot(None),
    )

    stmt = stmt.where(Problem.difficulty.between(
        max(1, target_difficulty - 1),
        min(10, target_difficulty + 1),
    ))

    seven_days_ago = now - timedelta(days=7)
    recent_subquery = (
        select(StudentAttempt.problem_id)
        .where(
            StudentAttempt.student_id == student_id,
            StudentAttempt.created_at >= seven_days_ago,
        )
    )
    stmt = stmt.where(not_(Problem.id.in_(recent_subquery)))

    if session_problem_ids:
        stmt = stmt.where(not_(Problem.id.in_(session_problem_ids)))

    stmt = stmt.order_by(Problem.difficulty).limit(1)

    result = await db.execute(stmt)
    return result.scalar_one_or_none()
