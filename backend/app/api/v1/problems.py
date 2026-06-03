from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select

from app.agents import run_agent
from app.api.deps import DbSession, get_current_user
from app.models.learning import LearningSession, StudentAttempt
from app.models.user import User
from app.schemas.problem import AttemptRequest, AttemptResponse, ProblemResponse
from app.services import problem_service

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("", response_model=list[ProblemResponse])
async def list_problems(
    db: DbSession,
    current_user: User = Depends(get_current_user),
    subject: str | None = None,
    knowledge_point_id: UUID | None = None,
    difficulty: int | None = None,
    limit: int = 20,
    offset: int = 0,
):
    problems = await problem_service.list_problems(
        db, subject=subject, knowledge_point_id=knowledge_point_id, difficulty=difficulty, limit=limit, offset=offset
    )
    return problems


@router.get("/{problem_id}", response_model=ProblemResponse)
async def get_problem(problem_id: UUID, db: DbSession, current_user: User = Depends(get_current_user)):
    problem = await problem_service.get_problem(db, problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


@router.post("/{problem_id}/attempt", response_model=AttemptResponse)
async def submit_attempt(
    problem_id: UUID,
    body: AttemptRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    if body.session_id is not None:
        session_id = body.session_id
    else:
        session = LearningSession(
            student_id=current_user.id,
            session_type="practice",
            subject="general",
            started_at=datetime.now(timezone.utc),
        )
        db.add(session)
        await db.flush()
        session_id = session.id

    agent_result = await run_agent(
        session_id=session_id,
        student_id=current_user.id,
        user_message=body.answer,
        request_type="attempt",
        problem_id=problem_id,
        student_answer=body.answer,
        db_session=db,
    )

    # Query for the attempt persisted by the agent's _response_node
    result = await db.execute(
        select(StudentAttempt)
        .where(
            StudentAttempt.student_id == current_user.id,
            StudentAttempt.problem_id == problem_id,
        )
        .order_by(StudentAttempt.created_at.desc())
        .limit(1)
    )
    attempt = result.scalar_one_or_none()

    if attempt is None:
        # Fallback: agent didn't create attempt (shouldn't happen)
        structured = agent_result.get("structured_data", {}) or {}
        attempt = StudentAttempt(
            session_id=session_id,
            student_id=current_user.id,
            problem_id=problem_id,
            answer=body.answer,
            is_correct=structured.get("is_correct"),
            ai_feedback=agent_result.get("agent_response"),
            error_type=structured.get("error_type"),
            hint_level_used=0,
            attempt_number=1,
        )
        db.add(attempt)
        await db.flush()

    return AttemptResponse(
        id=attempt.id,
        is_correct=attempt.is_correct,
        ai_feedback=attempt.ai_feedback,
        error_type=attempt.error_type,
        attempt_number=attempt.attempt_number,
    )
