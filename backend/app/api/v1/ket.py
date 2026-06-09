from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request

from app.api.deps import DbSession, get_current_user
from app.models.user import User
from app.schemas.ket import (
    KETQuestionListResponse,
    KETQuestionResponse,
    KETWritingScoreResponse,
    KETWritingSubmitRequest,
    KETWritingTaskResponse,
    KETSpeakingScoreResponse,
    KETSpeakingSubmitRequest,
    KETSpeakingTaskResponse,
)
from app.services import ket_service
from app.core.rate_limit import limiter

router = APIRouter(prefix="/ket", tags=["ket"])


@router.get("/questions", response_model=KETQuestionListResponse)
@limiter.limit("60/minute")
async def list_questions(
    request: Request,
    db: DbSession,
    current_user: User = Depends(get_current_user),
    skill: str | None = None,
    limit: int = 20,
    offset: int = 0,
):
    items, total = await ket_service.list_questions(db, skill=skill, limit=limit, offset=offset)
    return KETQuestionListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/questions/{question_id}", response_model=KETQuestionResponse)
@limiter.limit("60/minute")
async def get_question(
    request: Request,
    question_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    question = await ket_service.get_question(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


@router.get("/writing/tasks", response_model=list[KETWritingTaskResponse])
@limiter.limit("60/minute")
async def list_writing_tasks(
    request: Request,
    db: DbSession,
    current_user: User = Depends(get_current_user),
    task_type: str | None = None,
    limit: int = 20,
):
    return await ket_service.list_writing_tasks(db, task_type=task_type, limit=limit)


@router.get("/speaking/tasks", response_model=list[KETSpeakingTaskResponse])
@limiter.limit("60/minute")
async def list_speaking_tasks(
    request: Request,
    db: DbSession,
    current_user: User = Depends(get_current_user),
    difficulty: str | None = None,
    limit: int = 20,
):
    return await ket_service.list_speaking_tasks(db, difficulty=difficulty, limit=limit)


@router.post("/writing/submit", response_model=KETWritingScoreResponse)
@limiter.limit("30/minute")
async def submit_writing(
    request: Request,
    body: KETWritingSubmitRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    task = await ket_service.get_writing_task(db, body.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Writing task not found")
    result = await ket_service.score_writing(db, task, body.content, body.word_count)
    return KETWritingScoreResponse(**result)


@router.post("/speaking/submit", response_model=KETSpeakingScoreResponse)
@limiter.limit("30/minute")
async def submit_speaking(
    request: Request,
    body: KETSpeakingSubmitRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    task = await ket_service.get_speaking_task(db, body.task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Speaking task not found")
    result = await ket_service.score_speaking(db, task, body.transcript, body.audio_duration_sec)
    return KETSpeakingScoreResponse(**result)
