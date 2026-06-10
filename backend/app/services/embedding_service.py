"""Embedding generation and similarity search via pgvector."""
import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.llm import get_embedding_model
from app.models.knowledge import KnowledgePoint
from app.models.problem import Problem

logger = logging.getLogger(__name__)


async def generate_embedding(text: str) -> list[float] | None:
    model = get_embedding_model()
    if model is None:
        logger.debug("Embedding model unavailable")
        return None
    try:
        result = await model.aembed_query(text)
        return result
    except Exception:
        logger.warning("Embedding generation failed", exc_info=True)
        return None


async def generate_problem_embedding(
    problem_id: UUID, db: AsyncSession
) -> bool:
    stmt = select(Problem).where(Problem.id == problem_id)
    result = await db.execute(stmt)
    problem = result.scalar_one_or_none()
    if problem is None:
        return False

    parts = [problem.question_markdown]
    if problem.correct_answer:
        parts.append(problem.correct_answer)
    content = " ".join(parts)

    embedding = await generate_embedding(content)
    if embedding is None:
        return False

    problem.embedding = embedding
    await db.flush()
    return True


async def generate_knowledge_point_embedding(
    kp_id: UUID, db: AsyncSession
) -> bool:
    stmt = select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
    result = await db.execute(stmt)
    kp = result.scalar_one_or_none()
    if kp is None:
        return False

    parts = [kp.name]
    if kp.name_en:
        parts.append(kp.name_en)
    if kp.description:
        parts.append(kp.description)
    content = " ".join(parts)

    embedding = await generate_embedding(content)
    if embedding is None:
        return False

    kp.embedding = embedding
    await db.flush()
    return True


async def find_similar_problems(
    db: AsyncSession, query: str, limit: int = 5
) -> list[Problem]:
    embedding = await generate_embedding(query)
    if embedding is None:
        return []

    bind = db.get_bind()
    if bind.dialect.name != "postgresql":
        return []

    stmt = (
        select(Problem)
        .where(Problem.embedding.isnot(None))
        .order_by(Problem.embedding.cosine_distance(str(embedding)))
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def backfill_problem_embeddings(db: AsyncSession) -> int:
    stmt = select(Problem).where(Problem.embedding.is_(None))
    result = await db.execute(stmt)
    problems = list(result.scalars().all())

    count = 0
    for problem in problems:
        ok = await generate_problem_embedding(problem.id, db)
        if ok:
            count += 1
    await db.commit()
    return count


async def backfill_knowledge_point_embeddings(db: AsyncSession) -> int:
    stmt = select(KnowledgePoint).where(KnowledgePoint.embedding.is_(None))
    result = await db.execute(stmt)
    kps = list(result.scalars().all())

    count = 0
    for kp in kps:
        ok = await generate_knowledge_point_embedding(kp.id, db)
        if ok:
            count += 1
    await db.commit()
    return count
