from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    email: str | None = None
    phone: str | None = None
    name: str
    password: str
    role: str = "student"


class UserResponse(BaseModel):
    id: UUID
    email: str | None
    phone: str | None
    name: str
    role: str
    avatar_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class StudentProfileResponse(BaseModel):
    id: UUID
    user_id: UUID
    grade_level: int | None
    target_exam: str | None
    target_date: str | None
    daily_goal_minutes: int
    timezone: str
    preferred_lang: str
    diagnostic_done: bool
    xp_total: int
    streak_days: int
    longest_streak: int

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    username: str
    email: str | None = None
    password: str
    display_name: str | None = None
