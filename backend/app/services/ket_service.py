import json
import logging
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.llm import get_llm, is_llm_available
from app.models.ket import KETQuestion, KETWritingTask, KETSpeakingTask

logger = logging.getLogger(__name__)


async def list_questions(
    db: AsyncSession,
    skill: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> tuple[list[KETQuestion], int]:
    stmt = select(KETQuestion)
    count_stmt = select(func.count()).select_from(KETQuestion)
    if skill:
        stmt = stmt.where(KETQuestion.skill == skill)
        count_stmt = count_stmt.where(KETQuestion.skill == skill)
    total_result = await db.execute(count_stmt)
    total = total_result.scalar_one()
    stmt = stmt.order_by(KETQuestion.created_at.desc()).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def get_question(db: AsyncSession, question_id: UUID) -> KETQuestion | None:
    stmt = select(KETQuestion).where(KETQuestion.id == question_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_writing_tasks(
    db: AsyncSession,
    task_type: str | None = None,
    limit: int = 20,
) -> list[KETWritingTask]:
    stmt = select(KETWritingTask)
    if task_type:
        stmt = stmt.where(KETWritingTask.task_type == task_type)
    stmt = stmt.order_by(KETWritingTask.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_writing_task(db: AsyncSession, task_id: UUID) -> KETWritingTask | None:
    stmt = select(KETWritingTask).where(KETWritingTask.id == task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def list_speaking_tasks(
    db: AsyncSession,
    difficulty: str | None = None,
    limit: int = 20,
) -> list[KETSpeakingTask]:
    stmt = select(KETSpeakingTask)
    if difficulty:
        stmt = stmt.where(KETSpeakingTask.difficulty == difficulty)
    stmt = stmt.order_by(KETSpeakingTask.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_speaking_task(db: AsyncSession, task_id: UUID) -> KETSpeakingTask | None:
    stmt = select(KETSpeakingTask).where(KETSpeakingTask.id == task_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def score_writing(
    db: AsyncSession,
    task: KETWritingTask,
    content: str,
    word_count: int,
) -> dict:
    if word_count < task.word_limit_min:
        return {
            "score": 0,
            "content_score": 0,
            "organization_score": 0,
            "language_score": 0,
            "feedback": f"Word count ({word_count}) is below the minimum ({task.word_limit_min}).",
            "band": 0,
        }
    if word_count > task.word_limit_max * 2:
        return {
            "score": 0,
            "content_score": 0,
            "organization_score": 0,
            "language_score": 0,
            "feedback": f"Word count ({word_count}) exceeds the maximum ({task.word_limit_max}).",
            "band": 0,
        }

    if is_llm_available():
        llm = get_llm("strong")
        if llm is not None:
            prompt = (
                "You are a Cambridge A2 Key (KET) writing examiner. "
                "Rate the following writing response on the Cambridge English Scale (0-5 band).\n\n"
                f"Task type: {task.task_type}\n"
                f"Prompt: {task.prompt}\n"
                f"Word count: {word_count} (limit: {task.word_limit_min}-{task.word_limit_max})\n"
                f"Student response: {content}\n\n"
                "Respond ONLY with valid JSON: "
                '{"score": <0-100>, "content_score": <0-100>, "organization_score": <0-100>, '
                '"language_score": <0-100>, "feedback": "<brief feedback>", "band": <0-5.0>}'
            )
            try:
                from langchain_core.messages import HumanMessage
                response = await llm.ainvoke([HumanMessage(content=prompt)])
                text = response.content
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(text[start:end])
                    return {
                        "score": float(parsed.get("score", 50)),
                        "content_score": float(parsed.get("content_score", 50)),
                        "organization_score": float(parsed.get("organization_score", 50)),
                        "language_score": float(parsed.get("language_score", 50)),
                        "feedback": parsed.get("feedback", ""),
                        "band": float(parsed.get("band", 3.0)),
                    }
            except Exception as e:
                logger.warning("LLM scoring failed, using fallback: %s", e)

    return _writing_fallback(content, word_count, task.word_limit_min, task.word_limit_max)


def _writing_fallback(content: str, word_count: int, min_words: int, max_words: int) -> dict:
    length_ratio = min(word_count / max_words, 1.0)
    base_score = 40 + length_ratio * 30
    has_punctuation = any(c in content for c in ".!?,;")
    org_bonus = 10 if has_punctuation else 0
    sentence_count = max(content.count("."), 1)
    avg_sentence_len = word_count / sentence_count
    lang_bonus = 10 if 5 <= avg_sentence_len <= 20 else 0
    score = min(base_score + org_bonus + lang_bonus, 100)
    band = min(score / 20, 5.0)
    return {
        "score": round(score, 1),
        "content_score": round(base_score, 1),
        "organization_score": round(base_score + org_bonus, 1),
        "language_score": round(base_score + lang_bonus, 1),
        "feedback": f"Auto-evaluated: {word_count} words. " + (
            "Good effort!" if band >= 3.0 else "Try to use more varied vocabulary and sentence structures."
        ),
        "band": round(band, 1),
    }


async def score_speaking(
    db: AsyncSession,
    task: KETSpeakingTask,
    transcript: str,
    audio_duration_sec: int,
) -> dict:
    if not transcript.strip():
        return {
            "score": 0,
            "band": 0,
            "feedback": "No transcript provided. Please try again.",
        }

    if is_llm_available():
        llm = get_llm("strong")
        if llm is not None:
            prompt = (
                "You are a Cambridge A2 Key (KET) speaking examiner. "
                "Rate the following speaking transcript.\n\n"
                f"Topic: {task.topic}\n"
                f"Question: {task.question}\n"
                f"Difficulty: {task.difficulty}\n"
                f"Audio duration: {audio_duration_sec} seconds "
                f"(expected: {task.expected_duration_sec} sec)\n"
                f"Transcript: {transcript}\n\n"
                "Respond ONLY with valid JSON: "
                '{"score": <0-100>, "band": <0-5.0>, "feedback": "<brief feedback>"}'
            )
            try:
                from langchain_core.messages import HumanMessage
                response = await llm.ainvoke([HumanMessage(content=prompt)])
                text = response.content
                start = text.find("{")
                end = text.rfind("}") + 1
                if start >= 0 and end > start:
                    parsed = json.loads(text[start:end])
                    return {
                        "score": float(parsed.get("score", 50)),
                        "band": float(parsed.get("band", 3.0)),
                        "feedback": parsed.get("feedback", ""),
                    }
            except Exception as e:
                logger.warning("LLM speaking scoring failed, using fallback: %s", e)

    return _speaking_fallback(transcript, audio_duration_sec, task.expected_duration_sec)


def _speaking_fallback(transcript: str, audio_duration_sec: int, expected_duration: int) -> dict:
    words = transcript.split()
    word_count = len(words)
    duration_ratio = min(audio_duration_sec / max(expected_duration, 1), 1.5)
    length_score = min(word_count / 30, 1.0) * 40
    duration_score = duration_ratio * 30
    vocab_variety = len(set(words)) / max(word_count, 1)
    vocab_score = vocab_variety * 30
    score = min(length_score + duration_score + vocab_score, 100)
    band = min(score / 20, 5.0)
    return {
        "score": round(score, 1),
        "band": round(band, 1),
        "feedback": f"Auto-evaluated: {word_count} words in {audio_duration_sec}s. " + (
            "Good response!" if band >= 3.0 else "Try to speak more and use varied vocabulary."
        ),
    }
