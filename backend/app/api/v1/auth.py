from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select
from uuid import UUID

from app.api.deps import DbSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import StudentProfile, User
from app.schemas.user import LoginRequest, RefreshTokenRequest, RegisterRequest, TokenResponse
from app.core.rate_limit import limiter

router = APIRouter()


@router.post("/login")
@limiter.limit("5/minute")
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
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", status_code=201)
@limiter.limit("3/minute")
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
    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)
