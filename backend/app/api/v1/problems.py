from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession
from app.schemas.problem import AttemptRequest, AttemptResponse, ProblemResponse

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=list[ProblemResponse])
async def list_problems(
    db: DbSession,
    subject: str | None = None,
    knowledge_point_id: UUID | None = None,
    difficulty: int | None = None,
    limit: int = 20,
    offset: int = 0,
):
    ...


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(problem_id: UUID, db: DbSession):
    ...


@router.post("/{problem_id}/attempt", response_model=AttemptResponse)
async def submit_attempt(
    problem_id: UUID, body: AttemptRequest, db: DbSession
):
    ...
