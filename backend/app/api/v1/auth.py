import logging
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Cookie, HTTPException, Request, Response, status
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

ACCESS_COOKIE_NAME = "access_token"
REFRESH_COOKIE_NAME = "refresh_token"
COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 7 days (matches refresh token)


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    response.set_cookie(
        key=ACCESS_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=60 * 60,  # 1 hour, matches access token
        path="/",
    )
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production",
        samesite="lax",
        max_age=COOKIE_MAX_AGE,
        path="/",
    )


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
async def login(request: Request, response: Response, body: LoginRequest, db: DbSession) -> TokenResponse:
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
    _set_auth_cookies(response, access_token, refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/register", status_code=201)
@limiter.limit("100/minute" if settings.DISABLE_REDIS else "3/minute")
async def register(request: Request, response: Response, body: RegisterRequest, db: DbSession) -> TokenResponse:
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
    _set_auth_cookies(response, access_token, refresh_token)
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh")
async def refresh_token(
    db: DbSession,
    response: Response,
    body: RefreshTokenRequest | None = None,
    refresh_token_cookie: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME),
) -> TokenResponse:
    # Read refresh token from body (Bearer/API clients) or cookie (browser)
    refresh_token_value = None
    if body and body.refresh_token:
        refresh_token_value = body.refresh_token
    elif refresh_token_cookie:
        refresh_token_value = refresh_token_cookie

    if not refresh_token_value:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token",
        )

    payload = decode_refresh_token(refresh_token_value)
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
    _set_auth_cookies(response, access_token, new_refresh_token)
    logger.info("Refresh token rotated for user=%s", user_id)
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_token)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(ACCESS_COOKIE_NAME, path="/")
    response.delete_cookie(REFRESH_COOKIE_NAME, path="/")
    return {"message": "Logged out"}
