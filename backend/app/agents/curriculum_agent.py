"""Curriculum node: course scheduling, recommendations, FSRS reviews."""
import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from langchain_core.messages import HumanMessage, SystemMessage

from app.agents.llm import get_llm, is_llm_available
from app.agents.prompts import get_system_prompt
from app.agents.state import AgentState
from app.agents.services.problem_selector import select_next_problem

logger = logging.getLogger(__name__)

# Pillar groupings by subject for mastery breakdown
_SUBJECT_PILLARS = {
    "amc_math": {
        "algebra": ["algebra", "equations", "inequalities", "functions", "sequences"],
        "geometry": ["geometry", "triangles", "circles", "coordinate", "area", "volume"],
        "counting": ["counting", "probability", "combinatorics", "permutations"],
        "number_theory": ["number_theory", "divisibility", "primes", "modular", "integers"],
    },
    "ket_english": {
        "reading": ["reading", "comprehension", "vocabulary"],
        "writing": ["writing", "grammar", "spelling", "sentence"],
        "listening": ["listening", "audio", "phonetics"],
        "speaking": ["speaking", "pronunciation", "oral", "conversation"],
    },
    "chn_composition": {
        "writing": ["composition", "essay", "narrative", "argumentative"],
        "reading": ["reading", "comprehension", "analysis"],
    },
    "chn_poetry": {
        "recitation": ["recitation", "memorization"],
        "appreciation": ["appreciation", "analysis", "imagery"],
    },
}


async def curriculum_node(state: AgentState) -> dict:
    """
    Handle curriculum-related requests:
    - Session initialization (recommend starting point)
    - Next problem selection (adaptive)
    - Review scheduling (FSRS)
    - Progress summary
    """
    intent = state.get("intent", "manage")
    knowledge_states = state.get("knowledge_states", [])
    student = state.get("student", {})

    if intent == "manage" and state.get("request_type") == "session_init":
        return await _handle_session_init(state, knowledge_states, student)

    if intent == "practice":
        return await _handle_next_problem(state, knowledge_states, student)

    # General management/progress query
    return await _handle_general(state, knowledge_states, student)


# ---------------------------------------------------------------------------
# Session initialisation
# ---------------------------------------------------------------------------

async def _handle_session_init(state, knowledge_states, student) -> dict:
    """Recommend starting point for new session — LLM-enhanced with rule-based fallback."""
    now = datetime.now(timezone.utc)

    due_reviews = [
        ks for ks in knowledge_states
        if ks.get("next_review") and
           datetime.fromisoformat(ks["next_review"]) <= now
    ]

    weak = [ks for ks in knowledge_states if 0 < ks["mastery"] < 0.4]

    if is_llm_available():
        try:
            result = await _llm_session_init(state, knowledge_states, student, due_reviews, weak, now)
            if result is not None:
                return result
        except Exception:
            logger.warning("LLM session init failed, falling back to rules", exc_info=True)

    # Rule-based fallback (preserves original behaviour)
    return _rule_based_session_init(due_reviews, weak)


async def _llm_session_init(state, knowledge_states, student, due_reviews, weak, now) -> dict | None:
    """Build rich context and call LLM for session-start recommendation."""
    llm = get_llm("fast")
    if llm is None:
        return None

    subject = state.get("subject", "amc_math")
    student_name = student.get("name", "Student")
    grade_level = student.get("grade_level", "Unknown")
    target_exam = student.get("target_exam", "Not set")
    preferred_lang = student.get("preferred_lang", "en")

    knowledge_summary = _build_knowledge_summary(knowledge_states)
    due_reviews_summary = _build_due_reviews_summary(due_reviews)
    weak_areas_detail = _build_weak_areas_detail(weak)
    learning_trends = _build_learning_trends(knowledge_states)
    time_of_day = now.strftime("%Y-%m-%d %H:%M UTC")
    daily_goal_progress = _compute_daily_goal_progress(knowledge_states)

    system_prompt = get_system_prompt(
        "curriculum_session_init",
        student_name=student_name,
        grade_level=grade_level,
        target_exam=target_exam,
        subject=subject,
        preferred_lang=preferred_lang,
        knowledge_summary=knowledge_summary,
        due_reviews_summary=due_reviews_summary,
        weak_areas_detail=weak_areas_detail,
        learning_trends=learning_trends,
        time_of_day=time_of_day,
        daily_goal_progress=daily_goal_progress,
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content="Start my session."),
    ]
    response = await llm.ainvoke(messages)

    try:
        content = response.content.strip()
        if content.startswith("```"):
            content = content.split("\n", 1)[1] if "\n" in content else content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
        parsed = json.loads(content)
    except (json.JSONDecodeError, IndexError):
        logger.warning("Failed to parse LLM session init JSON, returning raw content")
        parsed = None

    if parsed and isinstance(parsed, dict):
        greeting = parsed.get("greeting", "Welcome back!")
        motivational = parsed.get("motivational_note", "")
        message = f"{greeting}\n\n{motivational}" if motivational else greeting

        return {
            "agent_response": message,
            "structured_data": {
                "due_reviews": len(due_reviews),
                "weak_areas": len(weak),
                "recommendation": parsed.get("recommendation_type", "review" if due_reviews else "learn_new"),
                "focus_topics": parsed.get("focus_topics", []),
                "estimated_duration_minutes": parsed.get("estimated_duration_minutes", 25),
                "reasoning": parsed.get("reasoning", ""),
                "suggested_order": parsed.get("suggested_order", []),
            },
            "model_used": "fast",
        }

    return {
        "agent_response": response.content,
        "structured_data": {
            "due_reviews": len(due_reviews),
            "weak_areas": len(weak),
            "recommendation": "review" if due_reviews else "learn_new",
        },
        "model_used": "fast",
    }


def _rule_based_session_init(due_reviews, weak) -> dict:
    """Rule-based fallback for session init (original logic)."""
    response_parts = []
    if due_reviews:
        response_parts.append(
            f"You have {len(due_reviews)} knowledge points due for review."
        )
    if weak:
        response_parts.append(
            "Your weakest areas need attention (mastery < 40%)."
        )

    message = " ".join(response_parts) if response_parts else (
        "Welcome! Let's find the right starting point for you."
    )

    return {
        "agent_response": message,
        "structured_data": {
            "due_reviews": len(due_reviews),
            "weak_areas": len(weak),
            "recommendation": "review" if due_reviews else "learn_new",
        },
    }


# ---------------------------------------------------------------------------
# Next problem selection (unchanged)
# ---------------------------------------------------------------------------

async def _handle_next_problem(state, knowledge_states, student) -> dict:
    """Select next problem based on adaptive strategy."""
    from uuid import UUID

    student_id = state.get("student_id")
    subject = state.get("subject", "amc_math")
    target_exam = student.get("target_exam", "AMC8")

    session_problem_ids = _get_session_problem_ids(state)

    db = state.get("db_session")
    if db is None:
        from app.db.session import async_session_factory
        async with async_session_factory() as db:
            problem = await select_next_problem(
                db=db,
                student_id=UUID(str(student_id)),
                subject=subject,
                target_exam=target_exam,
                knowledge_states=knowledge_states,
                session_problem_ids=session_problem_ids,
            )
    else:
        problem = await select_next_problem(
            db=db,
            student_id=UUID(str(student_id)),
            subject=subject,
            target_exam=target_exam,
            knowledge_states=knowledge_states,
            session_problem_ids=session_problem_ids,
        )

    if problem:
        return {
            "agent_response": f"Here's your next problem:\n\n{problem.question_markdown}",
            "structured_data": {
                "next_problem_id": str(problem.id),
                "difficulty": problem.difficulty,
            },
        }

    return {
        "agent_response": "No more problems available for this topic right now. Try a different area!",
    }


def _get_session_problem_ids(state) -> list[UUID] | None:
    """Extract attempted problem IDs from session messages metadata."""
    session_messages = state.get("session_messages", [])
    if not session_messages:
        return None
    ids = []
    for msg in session_messages:
        meta = msg.get("metadata") or msg.get("metadata_") or {}
        pid = meta.get("problem_id")
        if pid:
            try:
                ids.append(UUID(str(pid)))
            except (ValueError, AttributeError):
                continue
    return ids if ids else None


# ---------------------------------------------------------------------------
# General progress / curriculum queries
# ---------------------------------------------------------------------------

async def _handle_general(state, knowledge_states, student) -> dict:
    """Handle general curriculum queries — LLM-enhanced with static fallback."""
    if not is_llm_available():
        return {
            "agent_response": "Curriculum features require an internet connection.",
        }

    try:
        return await _llm_general(state, knowledge_states, student)
    except Exception:
        logger.warning("LLM general query failed, falling back to basic summary", exc_info=True)
        return _fallback_general(state, knowledge_states, student)


async def _llm_general(state, knowledge_states, student) -> dict:
    """Rich LLM-powered progress analysis."""
    llm = get_llm("fast")
    if llm is None:
        return _fallback_general(state, knowledge_states, student)

    subject = state.get("subject", "amc_math")
    student_name = student.get("name", "Student")
    grade_level = student.get("grade_level", "Unknown")
    target_exam = student.get("target_exam", "Not set")
    user_msg = state.get("user_message", "Show my progress")

    mastered_count = len(student.get("mastered_kps", []))
    total_kps = len(knowledge_states) if knowledge_states else 0
    pillar_breakdown = _build_pillar_breakdown(knowledge_states, subject)
    week_comparison = _build_week_comparison(knowledge_states)
    detailed_states = _build_detailed_knowledge_states(knowledge_states)

    system_prompt = get_system_prompt(
        "curriculum_progress",
        student_name=student_name,
        grade_level=grade_level,
        target_exam=target_exam,
        subject=subject,
        mastered_count=mastered_count,
        total_kps=total_kps,
        pillar_breakdown=pillar_breakdown,
        week_comparison=week_comparison,
        detailed_knowledge_states=detailed_states,
        user_question=user_msg,
    )

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_msg),
    ]
    response = await llm.ainvoke(messages)

    return {
        "agent_response": response.content,
        "structured_data": {
            "pillar_breakdown": _pillar_breakdown_dict(knowledge_states, subject),
            "mastered_count": mastered_count,
            "total_kps": total_kps,
        },
        "model_used": "fast",
    }


def _fallback_general(state, knowledge_states, student) -> dict:
    """Basic rule-based fallback when LLM unavailable."""
    summary = _build_progress_summary(knowledge_states, student)
    return {
        "agent_response": summary,
    }


# ---------------------------------------------------------------------------
# Context-building helpers
# ---------------------------------------------------------------------------

def _build_knowledge_summary(knowledge_states: list[dict]) -> str:
    """Build a concise text summary of all knowledge states."""
    if not knowledge_states:
        return "No knowledge states tracked yet."

    total = len(knowledge_states)
    mastered = sum(1 for ks in knowledge_states if ks["mastery"] >= 0.8)
    learning = sum(1 for ks in knowledge_states if 0.4 <= ks["mastery"] < 0.8)
    weak = sum(1 for ks in knowledge_states if 0 < ks["mastery"] < 0.4)
    unseen = sum(1 for ks in knowledge_states if ks["mastery"] == 0)

    avg_mastery = sum(ks["mastery"] for ks in knowledge_states) / total if total else 0
    lines = [
        f"Total tracked: {total} knowledge points",
        f"  Mastered (>=80%): {mastered}",
        f"  Learning (40-80%): {learning}",
        f"  Weak (<40%): {weak}",
        f"  Not started: {unseen}",
        f"  Average mastery: {avg_mastery:.0%}",
    ]
    return "\n".join(lines)


def _build_due_reviews_summary(due_reviews: list[dict]) -> str:
    if not due_reviews:
        return "No reviews due right now."
    lines = [f"{len(due_reviews)} knowledge points are due for review:"]
    for ks in due_reviews[:10]:
        topic = ks.get("knowledge_point_name") or ks.get("topic", "Unknown topic")
        mastery = ks.get("mastery", 0)
        stability = ks.get("stability", 0)
        lines.append(f"  - {topic}: mastery={mastery:.0%}, stability={stability:.1f} days")
    if len(due_reviews) > 10:
        lines.append(f"  ... and {len(due_reviews) - 10} more")
    return "\n".join(lines)


def _build_weak_areas_detail(weak_areas: list[dict]) -> str:
    """Detail the weakest knowledge areas."""
    if not weak_areas:
        return "No significantly weak areas detected."
    sorted_weak = sorted(weak_areas, key=lambda ks: ks["mastery"])
    lines = [f"{len(sorted_weak)} weak areas (mastery < 40%):"]
    for ks in sorted_weak[:8]:
        topic = ks.get("knowledge_point_name") or ks.get("topic", "Unknown topic")
        mastery = ks.get("mastery", 0)
        review_count = ks.get("review_count", 0)
        lines.append(f"  - {topic}: mastery={mastery:.0%}, reviews={review_count}")
    return "\n".join(lines)


def _build_learning_trends(knowledge_states: list[dict]) -> str:
    """Infer learning trends from knowledge state metadata."""
    if not knowledge_states:
        return "No trend data available yet."

    total = len(knowledge_states)
    high_stability = sum(1 for ks in knowledge_states if ks.get("stability", 0) > 14)
    improving = sum(1 for ks in knowledge_states if ks.get("mastery", 0) > 0.5 and ks.get("review_count", 0) > 3)
    needs_review = sum(
        1 for ks in knowledge_states
        if ks.get("next_review") and
           datetime.fromisoformat(ks["next_review"]) <= datetime.now(timezone.utc)
    )

    lines = [
        f"Knowledge points with strong retention (>14 days): {high_stability}/{total}",
        f"Knowledge points with solid practice (>3 reviews, >50% mastery): {improving}/{total}",
        f"Overdue for review: {needs_review}",
    ]
    if high_stability > total * 0.6:
        lines.append("Trend: Strong overall retention — student is building lasting knowledge.")
    elif improving > total * 0.4:
        lines.append("Trend: Good progress — several areas are consolidating.")
    else:
        lines.append("Trend: Early stage — focus on building foundational mastery.")
    return "\n".join(lines)


def _compute_daily_goal_progress(knowledge_states: list[dict]) -> str:
    """Estimate daily goal progress from today's activity."""
    today = datetime.now(timezone.utc).date()
    reviewed_today = 0
    for ks in knowledge_states:
        last_review = ks.get("next_review")
        if last_review:
            try:
                reviewed_today += 1
            except (ValueError, TypeError):
                pass

    total = len(knowledge_states)
    if total == 0:
        return "No data to estimate progress."
    return f"{reviewed_today} reviews tracked out of {total} total knowledge points."


def _build_pillar_breakdown(knowledge_states: list[dict], subject: str) -> str:
    """Build mastery breakdown by subject pillar."""
    if not knowledge_states:
        return "No knowledge data available for breakdown."

    pillars = _SUBJECT_PILLARS.get(subject, {})
    if not pillars:
        return _build_generic_pillar_text(knowledge_states)

    lines = []
    for pillar_name, keywords in pillars.items():
        matching = [
            ks for ks in knowledge_states
            if _ks_matches_pillar(ks, keywords)
        ]
        if matching:
            avg = sum(ks["mastery"] for ks in matching) / len(matching)
            count = len(matching)
            mastered = sum(1 for ks in matching if ks["mastery"] >= 0.8)
            lines.append(
                f"  {pillar_name.capitalize()}: avg mastery {avg:.0%} "
                f"({mastered}/{count} mastered)"
            )
        else:
            lines.append(f"  {pillar_name.capitalize()}: no data yet")

    return "\n".join(lines)


def _ks_matches_pillar(ks: dict, keywords: list[str]) -> bool:
    """Check if a knowledge state's topic matches any keyword in a pillar."""
    topic = (ks.get("knowledge_point_name") or ks.get("topic") or "").lower()
    return any(kw in topic for kw in keywords)


def _build_generic_pillar_text(knowledge_states: list[dict]) -> str:
    """Fallback pillar text when no subject-specific pillars exist."""
    by_level = {}
    for ks in knowledge_states:
        level = ks.get("mastery_level", "unknown")
        by_level.setdefault(level, []).append(ks)

    lines = []
    for level in ["mastered", "learning", "familiar", "unfamiliar", "unknown"]:
        states = by_level.get(level, [])
        if states:
            avg = sum(ks["mastery"] for ks in states) / len(states)
            lines.append(f"  {level.capitalize()}: {len(states)} topics (avg {avg:.0%})")
    return "\n".join(lines) if lines else "No breakdown available."


def _build_week_comparison(knowledge_states: list[dict]) -> str:
    """Build week-over-week comparison data."""
    if not knowledge_states:
        return "No historical data available for comparison."

    total = len(knowledge_states)
    avg_mastery = sum(ks["mastery"] for ks in knowledge_states) / total if total else 0
    avg_stability = sum(ks.get("stability", 0) for ks in knowledge_states) / total if total else 0
    total_reviews = sum(ks.get("review_count", 0) for ks in knowledge_states)

    lines = [
        f"Current average mastery: {avg_mastery:.0%}",
        f"Average memory stability: {avg_stability:.1f} days",
        f"Total review sessions: {total_reviews}",
        "Note: Detailed week-over-week comparison requires historical snapshots.",
    ]
    return "\n".join(lines)


def _build_detailed_knowledge_states(knowledge_states: list[dict]) -> str:
    """Build detailed list of knowledge states for LLM context."""
    if not knowledge_states:
        return "No detailed knowledge states available."

    sorted_states = sorted(knowledge_states, key=lambda ks: ks["mastery"])
    lines = []
    for ks in sorted_states[:20]:
        topic = ks.get("knowledge_point_name") or ks.get("topic", "Unknown")
        mastery = ks.get("mastery", 0)
        level = ks.get("mastery_level", "unknown")
        stability = ks.get("stability", 0)
        reviews = ks.get("review_count", 0)
        difficulty = ks.get("difficulty", "unknown")
        lines.append(
            f"  - {topic}: mastery={mastery:.0%}, level={level}, "
            f"stability={stability:.1f}d, reviews={reviews}, difficulty={difficulty}"
        )
    if len(sorted_states) > 20:
        lines.append(f"  ... and {len(sorted_states) - 20} more knowledge points")
    return "\n".join(lines)


def _pillar_breakdown_dict(knowledge_states: list[dict], subject: str) -> dict:
    """Return pillar breakdown as a structured dict for structured_data output."""
    pillars = _SUBJECT_PILLARS.get(subject, {})
    if not knowledge_states or not pillars:
        return {}

    result = {}
    for pillar_name, keywords in pillars.items():
        matching = [ks for ks in knowledge_states if _ks_matches_pillar(ks, keywords)]
        if matching:
            avg = sum(ks["mastery"] for ks in matching) / len(matching)
            result[pillar_name] = {
                "average_mastery": round(avg, 3),
                "total": len(matching),
                "mastered": sum(1 for ks in matching if ks["mastery"] >= 0.8),
            }
    return result


def _build_progress_summary(knowledge_states, student) -> str:
    """Build a text summary of student progress (original helper, enhanced)."""
    if not knowledge_states:
        return "No learning data yet."

    total = len(knowledge_states)
    avg_mastery = sum(ks["mastery"] for ks in knowledge_states) / total
    mastered = sum(1 for ks in knowledge_states if ks["mastery"] >= 0.8)
    weak = sum(1 for ks in knowledge_states if 0 < ks["mastery"] < 0.4)

    by_level = {}
    for ks in knowledge_states:
        level = ks.get("mastery_level", "unknown")
        by_level[level] = by_level.get(level, 0) + 1

    lines = [f"Student: {student.get('name', 'Unknown')}"]
    lines.append(f"Target: {student.get('target_exam', 'Not set')}")
    lines.append(f"Knowledge states: {total} tracked")
    lines.append(f"Overall mastery: {avg_mastery:.0%}")
    lines.append(f"Mastered: {mastered}, Weak: {weak}")
    for level, count in sorted(by_level.items()):
        lines.append(f"  {level}: {count}")

    return "\n".join(lines)
