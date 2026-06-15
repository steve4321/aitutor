"""Long-term student profile accumulation.

Extracts learning patterns from session summaries and updates
the StudentProfile aggregate metrics.
"""
import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.memory import SessionSummary
from app.models.user import StudentProfile

logger = logging.getLogger(__name__)

MAX_RECENT_SENTIMENTS = 20
MAX_PENDING_ITEMS = 10


async def update_student_profile_from_summary(
    db: AsyncSession,
    student_id: UUID,
    summary: SessionSummary,
) -> None:
    """Extract learning patterns from a session summary and update the student profile."""
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student_id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        return

    profile.session_count_total = (profile.session_count_total or 0) + 1
    _update_interaction_pattern(profile, summary)
    _update_emotional_trend(profile, summary)
    _update_learning_style(profile)
    _update_pending_items(profile, summary)
    profile.last_memory_update = datetime.now(timezone.utc)


def _update_interaction_pattern(profile: StudentProfile, summary: SessionSummary) -> None:
    style = summary.interaction_style or {}
    pattern = dict(profile.interaction_pattern or {})

    if style.get("response_detail"):
        pattern["response_detail"] = style["response_detail"]

    new_avg = style.get("hint_level_avg")
    if new_avg is not None and isinstance(new_avg, (int, float)):
        old_avg = pattern.get("hint_level_avg")
        if old_avg is None or profile.session_count_total <= 1:
            pattern["hint_level_avg"] = round(float(new_avg), 2)
        else:
            old_count = profile.session_count_total - 1
            pattern["hint_level_avg"] = round(
                (float(old_avg) * old_count + float(new_avg)) / profile.session_count_total,
                2,
            )

    if style.get("pacing"):
        pattern["pacing"] = style["pacing"]

    profile.interaction_pattern = pattern


def _update_emotional_trend(profile: StudentProfile, summary: SessionSummary) -> None:
    if not summary.sentiment:
        return
    trend = dict(profile.emotional_trend or {})
    recent = list(trend.get("recent_sentiments", []))
    recent.append(summary.sentiment)
    if len(recent) > MAX_RECENT_SENTIMENTS:
        recent = recent[-MAX_RECENT_SENTIMENTS:]
    trend["recent_sentiments"] = recent
    profile.emotional_trend = trend


def _update_learning_style(profile: StudentProfile) -> None:
    if profile.learning_style is not None:
        return
    if (profile.session_count_total or 0) < 3:
        return
    pattern = profile.interaction_pattern or {}
    detail = pattern.get("response_detail")
    if detail == "verbose":
        profile.learning_style = "reading"
    elif detail == "concise":
        profile.learning_style = "visual"


def _update_pending_items(profile: StudentProfile, summary: SessionSummary) -> None:
    if not summary.pending_items:
        return
    pattern = dict(profile.interaction_pattern or {})
    existing = list(pattern.get("pending_items", []))
    for item in summary.pending_items:
        if item not in existing:
            existing.append(item)
    if len(existing) > MAX_PENDING_ITEMS:
        existing = existing[-MAX_PENDING_ITEMS:]
    pattern["pending_items"] = existing
    profile.interaction_pattern = pattern
