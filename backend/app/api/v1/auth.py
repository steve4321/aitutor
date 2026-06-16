import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from uuid import UUID

from app.api.deps import DbSession
from app.core.security import (
    REFRESH_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.auth import RefreshToken
from app.models.user import StudentProfile, User
from app.schemas.user import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse
from app.core.rate_limit import limiter, RATE_LIMITS
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


async def _store_refresh_token(
    db: DbSession, token: str, user_id: UUID
) -> str:
    payload = decode_refresh_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to encode refresh token",
        )
    jti = payload["jti"]
    db.add(RefreshToken(
        jti=jti,
        user_id=user_id,
        used=False,
        expires_at=datetime.now(timezone.utc)
        + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES),
    ))
    await db.flush()
    return jti


@router.post("/login")
@limiter.limit(RATE_LIMITS["auth_login"])
async def login(request: Request, body: LoginRequest, db: DbSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.name == body.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    await _store_refresh_token(db, refresh_token, user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", status_code=201)
@limiter.limit("100/minute" if settings.DISABLE_REDIS else "3/minute")
async def register(request: Request, body: RegisterRequest, db: DbSession) -> TokenResponse:
    result = await db.execute(select(User).where(User.name == body.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    user = User(
        name=body.username,
        email=body.email or None,
        password_hash=hash_password(body.password),
        role="student",
    )
    db.add(user)
    await db.flush()

    profile = StudentProfile(
        user_id=user.id,
        preferred_lang="zh-CN",
    )
    db.add(profile)

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    await _store_refresh_token(db, refresh_token, user.id)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh_token(body: RefreshTokenRequest, db: DbSession) -> TokenResponse:
    payload = decode_refresh_token(body.refresh_token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    user_id = UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    jti = payload.get("jti")
    if jti:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.jti == jti)
        )
        token_record = result.scalar_one_or_none()
        if token_record is None:
            logger.warning("Unknown refresh token jti=%s for user=%s", jti, user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        if token_record.used:
            logger.warning(
                "Refresh token reuse detected: jti=%s user=%s", jti, user_id
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has expired",
            )
        token_record.used = True
        await db.flush()

    access_token = create_access_token({"sub": str(user.id)})
    new_refresh_token = create_refresh_token({"sub": str(user.id)})
    await _store_refresh_token(db, new_refresh_token, user.id)
    logger.info("Refresh token rotated for user=%s", user_id)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)
