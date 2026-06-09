from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select

from app.agents import run_agent
from app.api.deps import DbSession, get_current_user
from app.models.learning import LearningSession
from app.models.message import Message
from app.models.user import User
from app.schemas.chat import ChatMessageRequest, ChatMessageResponse
from app.core.rate_limit import limiter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message", response_model=ChatMessageResponse)
@limiter.limit("20/minute")
async def send_message(
    request: Request,
    body: ChatMessageRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    if body.session_id is not None:
        result = await db.execute(
            select(LearningSession).where(
                LearningSession.id == body.session_id,
                LearningSession.student_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        if session is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
    else:
        session = LearningSession(
            student_id=current_user.id,
            session_type="chat",
            subject="general",
            started_at=datetime.now(timezone.utc),
        )
        db.add(session)
        await db.flush()

    user_msg = Message(
        session_id=session.id,
        role="user",
        content=body.content,
        media=body.media,
    )
    db.add(user_msg)
    await db.flush()
    # Do NOT commit here — get_db dependency handles it, and agent layer has its own session

    agent_result = await run_agent(
        session_id=session.id,
        student_id=current_user.id,
        user_message=body.content,
        media=body.media,
        request_type="chat",
        db_session=db,
    )

    # Retrieve the assistant message by its deterministic ID (avoids race condition)
    message_id = agent_result.get("message_id")
    if message_id:
        ai_msg = await db.get(Message, message_id)
    else:
        ai_msg = None

    if ai_msg is None:
        # Agent didn't persist (edge case) — return response without DB record
        return ChatMessageResponse(
            id=user_msg.id,
            role="assistant",
            content=agent_result.get("agent_response", "Sorry, I couldn't process that."),
            session_id=session.id,
        )

    return ChatMessageResponse(
        id=ai_msg.id,
        role=ai_msg.role,
        content=ai_msg.content,
        session_id=session.id,
    )
