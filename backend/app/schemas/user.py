import re
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, field_validator


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
    target_date: date | None
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

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        if len(v) > 128:
            raise ValueError("Password must be at most 128 characters")
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
