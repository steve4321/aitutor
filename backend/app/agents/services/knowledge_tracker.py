"""Knowledge state update logic — bridges FSRS with DB models."""
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.learning import KnowledgeState
from app.agents.services.fsrs import (
    classify_mastery_level,
    update_difficulty,
    update_stability,
    calculate_retrievability,
    calculate_next_review,
    rating_from_correctness,
    initial_difficulty,
    initial_stability,
)
from app.agents.constants import MasteryConstants


def update_mastery(
    current_mastery: float,
    is_correct: bool,
    difficulty: float,
    hint_level: int = 0,
    problem_difficulty: int | None = None,
) -> float:
    """Calculate new mastery based on attempt result (§8.1 system-design.md)."""
    alpha = MasteryConstants.INCREMENT_CORRECT

    if is_correct:
        new_mastery = current_mastery + alpha * (1.0 - current_mastery)
    else:
        new_mastery = current_mastery * (1.0 - MasteryConstants.DECREMENT_INCORRECT * (1.0 / MasteryConstants.INCREMENT_CORRECT))

    if problem_difficulty and is_correct:
        bonus = max(0, (problem_difficulty - MasteryConstants.DIFFICULTY_BONUS_THRESHOLD) * MasteryConstants.DIFFICULTY_BONUS_MULTIPLIER)
        new_mastery += bonus

    hint_penalty = hint_level * MasteryConstants.HINT_PENALTY_PER_LEVEL
    new_mastery -= hint_penalty

    return max(0.0, min(1.0, new_mastery))


async def apply_knowledge_updates(
    db: AsyncSession,
    student_id: UUID,
    updates: list[dict],
) -> None:
    """Apply a batch of knowledge state updates to the DB."""
    for update in updates:
        kp_id = update.get("knowledge_point_id")
        if not kp_id:
            continue

        kp_uuid = UUID(str(kp_id)) if isinstance(kp_id, str) else kp_id

        result = await db.execute(
            select(KnowledgeState).where(
                KnowledgeState.student_id == student_id,
                KnowledgeState.knowledge_point_id == kp_uuid,
            )
        )
        state = result.scalar_one_or_none()

        if state is None:
            state = KnowledgeState(
                student_id=student_id,
                knowledge_point_id=kp_uuid,
                mastery=0.0,
                mastery_level="not_started",
                difficulty=5.0,
                stability=0.0,
                retrievability=1.0,
            )
            db.add(state)
            await db.flush()

        is_correct = update.get("is_correct", False)
        hint_level = update.get("hint_level_used", 0)
        fsrs_rating = update.get("fsrs_rating") or rating_from_correctness(is_correct, hint_level)

        now = datetime.now(timezone.utc)
        days_elapsed = 0
        if state.last_review:
            days_elapsed = (now - state.last_review).days

        if days_elapsed > 0 and state.stability > 0:
            retrievability = calculate_retrievability(state.stability, days_elapsed)
            state.mastery *= retrievability

        state.mastery = update_mastery(
            current_mastery=state.mastery,
            is_correct=is_correct,
            difficulty=state.difficulty,
            hint_level=hint_level,
        )

        if state.review_count == 0:
            state.difficulty = initial_difficulty(fsrs_rating)
            state.stability = initial_stability(fsrs_rating)
        else:
            state.difficulty = update_difficulty(state.difficulty, fsrs_rating)
            state.stability = update_stability(state.difficulty, state.stability, fsrs_rating)

        state.retrievability = calculate_retrievability(state.stability, 0)
        state.mastery_level = classify_mastery_level(state.mastery)
        state.next_review = calculate_next_review(state.stability, state.difficulty)
        state.last_review = now
        state.review_count += 1
        state.attempts += 1
        if is_correct:
            state.correct += 1
        else:
            state.lapse_count += 1
