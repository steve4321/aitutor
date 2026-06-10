import re
from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


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
    minutes_today: int = 0

    model_config = {"from_attributes": True}


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ProfileUpdateRequest(BaseModel):
    grade_level: int | None = None
    target_exam: str | None = None


class UserNameUpdateRequest(BaseModel):
    name: str


class ParentLinkRequest(BaseModel):
    link_code: str


class ParentLinkResponse(BaseModel):
    status: str
    parent_name: str | None = None


class RegisterRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    email: str | None = Field(default=None, max_length=255)
    password: str = Field(min_length=6, max_length=128)
    display_name: str | None = Field(default=None, max_length=100)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r"[A-Za-z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v
