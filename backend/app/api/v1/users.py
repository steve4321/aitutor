from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select

from app.api.deps import DbSession, get_current_user
from app.models.user import StudentProfile, User
from app.schemas.user import (
    ProfileUpdateRequest,
    StudentProfileResponse,
    UserNameUpdateRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    body: UserNameUpdateRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    if body.name is not None:
        current_user.name = body.name
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.get("/me/profile", response_model=StudentProfileResponse)
async def get_student_profile(
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    return profile


@router.patch("/me/profile", response_model=StudentProfileResponse)
async def update_student_profile(
    body: ProfileUpdateRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == current_user.id)
    )
    profile = result.scalar_one_or_none()
    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found",
        )
    if body.grade_level is not None:
        profile.grade_level = body.grade_level
    if body.target_exam is not None:
        profile.target_exam = body.target_exam
    await db.commit()
    await db.refresh(profile)
    return profile
