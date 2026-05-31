"""
Free Spaced Repetition Scheduler (FSRS) algorithm.
Simplified version based on open-spaced-repetition/fsrs4anki.
"""
import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


@dataclass
class FSRSParams:
    """Default FSRS parameters (can be tuned per student)."""
    w: tuple[float, ...] = (
        0.4,    # initial stability (again)
        0.6,    # initial stability (hard)
        2.4,    # initial stability (good)
        5.0,    # initial stability (easy)
        1.07,   # initial difficulty
        0.04,   # difficulty mean reversion
        1.48,   # difficulty decay
        0.10,   # stability increase base
        1.30,   # stability increase (hard)
        0.50,   # stability increase (good)
        0.04,   # stability increase (easy)
        0.25,   # hard penalty
        1.10,   # easy bonus
    )
    request_retention: float = 0.9


DEFAULT_PARAMS = FSRSParams()


def initial_stability(rating: int) -> float:
    """Get initial stability for a new item based on first rating (1-4)."""
    params = DEFAULT_PARAMS
    idx = max(0, min(3, rating - 1))
    return params.w[idx]


def initial_difficulty(rating: int) -> float:
    """Get initial difficulty for a new item."""
    params = DEFAULT_PARAMS
    d = params.w[4] - math.exp(params.w[5] * (rating - 1)) + 1
    return max(1.0, min(10.0, d))


def update_difficulty(difficulty: float, rating: int) -> float:
    """Update difficulty based on rating."""
    params = DEFAULT_PARAMS
    delta = params.w[6] * (initial_difficulty(3) - difficulty)
    new_d = difficulty - delta
    return max(1.0, min(10.0, new_d))


def update_stability(difficulty: float, stability: float, rating: int) -> float:
    """Update memory stability based on rating."""
    params = DEFAULT_PARAMS

    if stability <= 0:
        return initial_stability(max(rating, 2))

    if rating == 1:  # Again — memory lapsed
        new_s = max(0.1, stability * 0.5)
        return new_s

    # Successful recall
    hard_penalty = params.w[11] if rating == 2 else 1.0
    easy_bonus = params.w[12] if rating == 4 else 1.0

    increase = params.w[7] * (11 - difficulty) * easy_bonus * hard_penalty
    new_s = stability * (1 + increase)
    return max(0.1, min(365.0, new_s))


def calculate_retrievability(stability: float, elapsed_days: float) -> float:
    """
    Calculate current retrievability (recall probability).
    R = (1 + elapsed/stability * FACTOR)^(-1/DECAY)
    """
    if stability <= 0:
        return 0.0
    DECAY = -0.5
    FACTOR = 19.0 / 81.0
    return math.pow(1 + FACTOR * elapsed_days / stability, DECAY)


def calculate_next_review(
    stability: float,
    retention: float = 0.9,
) -> datetime:
    """Calculate the next review date based on FSRS parameters."""
    if stability <= 0:
        return datetime.now(timezone.utc) + timedelta(days=1)

    # Simplified: interval proportional to stability
    interval = max(1, min(365, int(round(stability * math.log(retention) / math.log(0.9)))))
    return datetime.now(timezone.utc) + timedelta(days=interval)


def classify_mastery_level(mastery: float) -> str:
    """Map mastery value to level string."""
    if mastery < 0.1:
        return "not_started"
    elif mastery < 0.3:
        return "attempted"
    elif mastery < 0.6:
        return "familiar"
    elif mastery < 0.85:
        return "proficient"
    else:
        return "mastered"


def rating_from_correctness(is_correct: bool, hint_level: int = 0) -> int:
    """Convert correctness + hint level to FSRS rating (1-4)."""
    if not is_correct:
        return 1  # Again
    if hint_level >= 3:
        return 2  # Hard
    if hint_level >= 1:
        return 3  # Good
    return 4  # Easy
