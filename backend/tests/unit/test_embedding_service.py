from unittest.mock import AsyncMock, patch

from app.services.embedding_service import (
    generate_embedding,
    generate_problem_embedding,
    generate_knowledge_point_embedding,
    find_similar_problems,
)
from app.models.problem import Problem


class TestGenerateEmbedding:
    async def test_returns_none_when_no_api_key(self):
        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=None,
        ):
            result = await generate_embedding("hello")
            assert result is None

    async def test_returns_embedding_vector(self):
        mock_model = AsyncMock()
        mock_model.aembed_query.return_value = [0.1] * 1536
        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=mock_model,
        ):
            result = await generate_embedding("hello")
            assert result is not None
            assert len(result) == 1536

    async def test_handles_llm_error_gracefully(self):
        mock_model = AsyncMock()
        mock_model.aembed_query.side_effect = RuntimeError("API error")
        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=mock_model,
        ):
            result = await generate_embedding("hello")
            assert result is None


class TestGenerateProblemEmbedding:
    async def test_returns_false_for_missing_problem(self, db_session):
        from uuid import uuid4

        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=None,
        ):
            ok = await generate_problem_embedding(uuid4(), db_session)
            assert ok is False

    async def test_stores_embedding_for_problem(self, db_session, knowledge_points):
        kp = knowledge_points[0]
        problem = Problem(
            subject="amc_math",
            format="mcq",
            question_markdown="What is 2+2?",
            correct_answer="4",
            difficulty=1,
            knowledge_point_ids=[str(kp.id)],
        )
        db_session.add(problem)
        await db_session.flush()

        mock_model = AsyncMock()
        mock_model.aembed_query.return_value = [0.1] * 1536
        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=mock_model,
        ):
            ok = await generate_problem_embedding(problem.id, db_session)
            assert ok is True
            assert problem.embedding is not None

    async def test_returns_false_when_no_model(self, db_session, knowledge_points):
        kp = knowledge_points[0]
        problem = Problem(
            subject="amc_math",
            format="mcq",
            question_markdown="test",
            difficulty=1,
            knowledge_point_ids=[str(kp.id)],
        )
        db_session.add(problem)
        await db_session.flush()

        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=None,
        ):
            ok = await generate_problem_embedding(problem.id, db_session)
            assert ok is False


class TestGenerateKnowledgePointEmbedding:
    async def test_returns_false_for_missing_kp(self, db_session):
        from uuid import uuid4

        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=None,
        ):
            ok = await generate_knowledge_point_embedding(uuid4(), db_session)
            assert ok is False

    async def test_stores_embedding_for_kp(self, db_session, knowledge_points):
        kp = knowledge_points[0]

        mock_model = AsyncMock()
        mock_model.aembed_query.return_value = [0.2] * 1536
        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=mock_model,
        ):
            ok = await generate_knowledge_point_embedding(kp.id, db_session)
            assert ok is True
            assert kp.embedding is not None


class TestFindSimilarProblems:
    async def test_returns_empty_when_no_model(self, db_session):
        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=None,
        ):
            results = await find_similar_problems(db_session, "test query")
            assert results == []

    async def test_returns_empty_for_sqlite(self, db_session):
        mock_model = AsyncMock()
        mock_model.aembed_query.return_value = [0.1] * 1536
        with patch(
            "app.services.embedding_service.get_embedding_model",
            return_value=mock_model,
        ):
            results = await find_similar_problems(db_session, "test query")
            assert results == []
