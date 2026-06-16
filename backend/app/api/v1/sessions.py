from datetime import datetime, timezone
from uuid import UUID

import logging
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user
from app.agents.services.memory import (
    generate_session_summary,
    save_session_summary,
)
from app.agents.services.profile_service import update_student_profile_from_summary
from app.core.rate_limit import limiter, RATE_LIMITS
from app.models.learning import LearningSession
from app.models.user import User
from app.schemas.session import SessionCreate, SessionResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
@limiter.limit(RATE_LIMITS["api_write"])
async def create_session(
    request: Request,
    body: SessionCreate,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    session = LearningSession(
        student_id=current_user.id,
        session_type=body.session_type,
        subject=body.subject,
        knowledge_point_id=body.knowledge_point_id,
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()
    return session


@router.post("/diagnostic", response_model=SessionResponse)
@limiter.limit(RATE_LIMITS["api_write"])
async def create_diagnostic_session(
    request: Request,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    logger.info("Diagnostic session started: user=%s", current_user.id)
    session = LearningSession(
        student_id=current_user.id,
        session_type="diagnostic",
        subject="math",
        started_at=datetime.now(timezone.utc),
    )
    db.add(session)
    await db.flush()
    return session


@router.post("/{session_id}/close", response_model=SessionResponse)
@limiter.limit(RATE_LIMITS["api_write"])
async def close_session(
    request: Request,
    session_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(LearningSession).where(
            LearningSession.id == session_id,
            LearningSession.student_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )

    if session.ended_at is None:
        now = datetime.now(timezone.utc)
        session.ended_at = now
        session.duration_sec = int(
            (now - session.started_at.replace(tzinfo=timezone.utc)).total_seconds()
        )

        try:
            summary_data = await generate_session_summary(
                db=db,
                session_id=session.id,
                student_id=current_user.id,
                subject=session.subject,
                session_type=session.session_type,
            )
            if summary_data:
                saved = await save_session_summary(
                    db=db,
                    session_id=session.id,
                    student_id=current_user.id,
                    summary_data=summary_data,
                    duration_min=(session.duration_sec or 0) // 60,
                )
                try:
                    await update_student_profile_from_summary(
                        db=db, student_id=current_user.id, summary=saved
                    )
                except Exception as e:
                    logger.warning("Profile update failed (non-blocking): %s", e)
        except Exception as e:
            logger.warning("Session summary generation failed (non-blocking): %s", e)

        await db.flush()
        await db.refresh(session)

    return session


@router.get("/{session_id}", response_model=SessionResponse)
@limiter.limit(RATE_LIMITS["api_read"])
async def get_session(
    request: Request,
    session_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(LearningSession).where(
            LearningSession.id == session_id,
            LearningSession.student_id == current_user.id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session
