from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession, get_current_user
from app.models.user import User
from app.schemas.user import StudentProfileResponse, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    ...


@router.get("/me/profile", response_model=StudentProfileResponse)
async def get_student_profile(current_user: User = Depends(get_current_user)):
    ...
