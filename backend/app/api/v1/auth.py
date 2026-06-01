from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from app.api.deps import DbSession
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.schemas.user import LoginRequest, RegisterRequest, TokenResponse
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
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)


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
    token = create_access_token({"sub": str(user.id)})
    return TokenResponse(access_token=token)
