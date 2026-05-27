from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(db: DbSession) -> User:
    # Placeholder: extract user from JWT, query DB
    raise NotImplementedError("Auth not implemented")
