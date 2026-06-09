from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select

from app.api.deps import DbSession, get_current_user
from app.models.learning import LearningSession
from app.models.user import StudentProfile, User
from app.schemas.user import (
    ProfileUpdateRequest,
    StudentProfileResponse,
    UserNameUpdateRequest,
    UserResponse,
)

router = APIRouter(prefix="/users", tags=["users"])


async def _build_profile_response(
    db: DbSession, profile: StudentProfile
) -> StudentProfileResponse:
    day_start = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    day_end = day_start.replace(hour=23, minute=59, second=59)
    minutes_result = await db.execute(
        select(func.coalesce(func.sum(LearningSession.duration_sec), 0)).where(
            LearningSession.student_id == profile.user_id,
            LearningSession.started_at >= day_start,
            LearningSession.started_at <= day_end,
        )
    )
    minutes_today = int(minutes_result.scalar() or 0) // 60
    return StudentProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        grade_level=profile.grade_level,
        target_exam=profile.target_exam,
        target_date=profile.target_date,
        daily_goal_minutes=profile.daily_goal_minutes,
        timezone=profile.timezone,
        preferred_lang=profile.preferred_lang,
        diagnostic_done=profile.diagnostic_done,
        xp_total=profile.xp_total,
        streak_days=profile.streak_days,
        longest_streak=profile.longest_streak,
        minutes_today=minutes_today,
    )


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
    return await _build_profile_response(db, profile)


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
    return await _build_profile_response(db, profile)
