from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("")
async def create_session(db: DbSession):
    ...


@router.get("/{session_id}")
async def get_session(session_id: UUID, db: DbSession):
    ...
