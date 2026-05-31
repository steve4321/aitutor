from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models.user import User


async def register_user(
    db: AsyncSession,
    email: str | None,
    phone: str | None,
    name: str,
    password: str,
    role: str = "student",
) -> User:
    result = await db.execute(select(User).where(User.name == name))
    existing_user = result.scalar_one_or_none()
    if existing_user is not None:
        raise ValueError(f"User with name '{name}' already exists")
    user = User(
        email=email,
        phone=phone,
        name=name,
        password_hash=hash_password(password),
        role=role,
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate_user(
    db: AsyncSession,
    login: str,
    password: str,
) -> User | None:
    result = await db.execute(select(User).where(User.name == login))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user
