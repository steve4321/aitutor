from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user
from app.models.learning import LearningSession
from app.models.user import User
from app.schemas.session import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
async def create_session(
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


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID, db: DbSession):
    result = await db.execute(
        select(LearningSession).where(LearningSession.id == session_id)
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found",
        )
    return session
