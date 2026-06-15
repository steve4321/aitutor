"""Session memory service: generate, persist, and load session summaries.

Used for cross-session memory injection into the AI teacher's prompt.
"""
import json
import logging
from datetime import datetime, timezone
from uuid import UUID

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.llm import get_llm, is_llm_available
from app.agents.prompts import get_system_prompt
from app.agents.tools import load_session_messages, load_student_context
from app.models.learning import LearningSession
from app.models.memory import SessionSummary

logger = logging.getLogger(__name__)


async def generate_session_summary(
    db: AsyncSession,
    session_id: UUID,
    student_id: UUID,
    subject: str,
    session_type: str,
) -> dict | None:
    """Generate a structured summary of a completed learning session via LLM."""
    if not is_llm_available():
        logger.warning("LLM not available, skipping summary generation")
        return None

    session = await db.get(LearningSession, session_id)
    if not session:
        return None

    duration_min = (session.duration_sec or 0) // 60
    messages = await load_session_messages(db, session_id, limit=50)
    student_ctx = await load_student_context(db, student_id)

    msgs_text = "\n".join(
        f"[{m['role']}]: {m['content'][:500]}" for m in messages[-30:]
    )

    profile_text = (
        f"name: {student_ctx.get('name', '')}, "
        f"grade: {student_ctx.get('grade_level', '')}, "
        f"target: {student_ctx.get('target_exam', '')}"
    )

    system_prompt = get_system_prompt(
        "session_summary",
        subject=subject,
        session_type=session_type,
        duration_minutes=duration_min,
        knowledge_state_before="{}",
        messages_content=msgs_text or "(no messages)",
        student_profile=profile_text,
        num_messages=len(messages),
    )

    llm = get_llm("fast")
    if llm is None:
        return None

    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content="Summarize this session."),
        ])
        result = json.loads(response.content.strip())
        return result
    except (json.JSONDecodeError, Exception) as e:
        logger.error("Failed to generate session summary: %s", e, exc_info=True)
        return None


async def save_session_summary(
    db: AsyncSession,
    session_id: UUID,
    student_id: UUID,
    summary_data: dict,
    duration_min: int | None = None,
    model_used: str | None = None,
) -> SessionSummary:
    """Persist a session summary to the database."""
    summary = SessionSummary(
        session_id=session_id,
        student_id=student_id,
        summary_text=summary_data.get("summary_text", ""),
        topics_discussed=summary_data.get("topics_discussed", []),
        knowledge_points_touched=summary_data.get("knowledge_points_touched", []),
        mastery_changes=summary_data.get("mastery_changes"),
        interaction_style=summary_data.get("interaction_style"),
        sentiment=summary_data.get("sentiment"),
        pending_items=summary_data.get("pending_items"),
        model_used=model_used,
        session_duration_min=duration_min,
        generated_at=datetime.now(timezone.utc),
    )
    db.add(summary)
    return summary


async def load_recent_summaries(
    db: AsyncSession,
    student_id: UUID,
    limit: int = 5,
) -> list[SessionSummary]:
    """Load the most recent session summaries for a student."""
    result = await db.execute(
        select(SessionSummary)
        .where(SessionSummary.student_id == student_id)
        .order_by(desc(SessionSummary.generated_at))
        .limit(limit)
    )
    return list(result.scalars().all())


def format_summaries_for_prompt(summaries: list[SessionSummary]) -> str:
    """Format session summaries into a condensed text block for prompt injection."""
    if not summaries:
        return "（暂无历史会话记录）"

    lines = []
    for i, s in enumerate(summaries, 1):
        ts = s.generated_at.strftime("%Y-%m-%d %H:%M") if s.generated_at else "未知时间"
        lines.append(f"### 会话 {i}（{ts}）")
        if s.summary_text:
            lines.append(f"摘要：{s.summary_text}")
        if s.topics_discussed:
            lines.append(f"讨论主题：{'、'.join(s.topics_discussed[:5])}")
        if s.sentiment:
            lines.append(f"学习状态：{s.sentiment}")
        if s.pending_items:
            lines.append(f"遗留事项：{'、'.join(s.pending_items[:3])}")
        lines.append("")
    return "\n".join(lines)


def summary_to_dict(s: SessionSummary) -> dict:
    """Convert a SessionSummary to a dict for AgentState consumption."""
    return {
        "id": str(s.id),
        "session_id": str(s.session_id),
        "summary_text": s.summary_text,
        "topics_discussed": s.topics_discussed or [],
        "knowledge_points_touched": s.knowledge_points_touched or [],
        "sentiment": s.sentiment,
        "pending_items": s.pending_items or [],
        "generated_at": s.generated_at.isoformat() if s.generated_at else None,
    }


async def build_student_memory_context(
    db: AsyncSession,
    student_id: UUID,
    subject: str = "amc_math",
    summary_limit: int = 3,
) -> str:
    """Build a unified student memory text block for prompt injection.

    Assembles L0 (recent summaries) and L1 (long-term profile) into a
    single Chinese-language string suitable for inclusion in any tutor prompt.
    """
    from app.models.user import StudentProfile

    parts: list[str] = []

    summaries = await load_recent_summaries(db, student_id, limit=summary_limit)
    if summaries:
        parts.append("## 最近学习记录")
        parts.append(format_summaries_for_prompt(summaries))

    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student_id)
    )
    profile = profile_result.scalar_one_or_none()
    if profile:
        profile_lines: list[str] = []
        if profile.learning_style:
            profile_lines.append(f"学习风格：{profile.learning_style}")
        if profile.pace_category:
            profile_lines.append(f"学习节奏：{profile.pace_category}")
        pattern = profile.interaction_pattern or {}
        if pattern.get("hint_level_avg"):
            profile_lines.append(f"平均提示求助级别：{pattern['hint_level_avg']}")
        if pattern.get("response_detail"):
            profile_lines.append(f"回答风格：{pattern['response_detail']}")
        if pattern.get("pacing"):
            profile_lines.append(f"本次节奏：{pattern['pacing']}")
        if pattern.get("common_mistakes"):
            mistakes = pattern["common_mistakes"][:3]
            profile_lines.append(
                f"常见错误：{'; '.join(m.get('pattern', '') for m in mistakes)}"
            )
        if pattern.get("pending_items"):
            profile_lines.append(
                f"待办遗留：{'; '.join(pattern['pending_items'][:3])}"
            )

        trend = profile.emotional_trend or {}
        if trend.get("recent_sentiments"):
            last_sentiment = trend["recent_sentiments"][-1]
            profile_lines.append(f"最近学习情绪：{last_sentiment}")
        if trend.get("confidence_trend"):
            profile_lines.append(f"信心趋势：{trend['confidence_trend']}")

        if profile_lines:
            parts.append("## 学生长期画像")
            for line in profile_lines:
                parts.append(f"- {line}")

    return "\n".join(parts) if parts else "（暂无长期学习数据）"


async def build_prerequisite_context(
    db: AsyncSession,
    student_id: UUID,
    current_kp_id: UUID | None = None,
) -> str:
    """Build prerequisite chain context for the current knowledge point.

    For each direct prerequisite of current_kp_id, shows the prerequisite's
    name and the student's current mastery, with a status icon.
    """
    if not current_kp_id:
        return ""

    from app.models.knowledge import KnowledgeDependency, KnowledgePoint
    from app.models.learning import KnowledgeState

    kp = await db.get(KnowledgePoint, current_kp_id)
    if not kp:
        return ""

    deps_result = await db.execute(
        select(KnowledgeDependency)
        .where(KnowledgeDependency.target_id == current_kp_id)
    )
    deps = deps_result.scalars().all()
    if not deps:
        return ""

    lines = [f"## 知识点上下文：{kp.name}"]
    if kp.pillar:
        lines.append(f"所属支柱：{kp.pillar}")

    prereq_lines = []
    for dep in deps:
        prereq = dep.prerequisite
        if not prereq:
            continue
        ks_result = await db.execute(
            select(KnowledgeState).where(
                KnowledgeState.student_id == student_id,
                KnowledgeState.knowledge_point_id == prereq.id,
            )
        )
        ks = ks_result.scalar_one_or_none()
        mastery = ks.mastery if ks else 0.0
        if mastery >= 0.8:
            icon = "✅"
        elif mastery >= 0.4:
            icon = "⚠️"
        else:
            icon = "❌"
        prereq_lines.append(
            f"- {prereq.code} {prereq.name}: 掌握度 {mastery:.0%} {icon}"
        )

    if prereq_lines:
        lines.append("前置知识依赖：")
        lines.extend(prereq_lines)

    return "\n".join(lines)
