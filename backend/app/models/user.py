from datetime import date, datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import JSON as JSONB, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("name", name="uq_users_name"),
    )

    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, nullable=True
    )
    phone: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # student, parent, admin
    avatar_url: Mapped[str | None] = mapped_column(Text, nullable=True)

    profile: Mapped["StudentProfile | None"] = relationship(
        "StudentProfile", back_populates="user", uselist=False,
        cascade="all, delete-orphan",
    )
    parent_links: Mapped[list["ParentLink"]] = relationship(
        "ParentLink", foreign_keys="ParentLink.parent_id", back_populates="parent",
        cascade="all, delete-orphan",
    )
    student_links: Mapped[list["ParentLink"]] = relationship(
        "ParentLink", foreign_keys="ParentLink.student_id", back_populates="student",
        cascade="all, delete-orphan",
    )
    preferences: Mapped["UserPreferences | None"] = relationship(
        "UserPreferences", back_populates="user", uselist=False,
        cascade="all, delete-orphan",
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    __table_args__ = ({"extend_existing": True},)

    user_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    grade_level: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    target_exam: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # AMC8, AMC10, AMC12, KET
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    daily_goal_minutes: Mapped[int] = mapped_column(
        SmallInteger, default=20
    )
    timezone: Mapped[str] = mapped_column(String(50), default="Asia/Shanghai")
    preferred_lang: Mapped[str] = mapped_column(String(10), default="zh-CN")
    diagnostic_done: Mapped[bool] = mapped_column(Boolean, default=False)
    diagnostic_result: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    xp_total: Mapped[int] = mapped_column(Integer, default=0)
    streak_days: Mapped[int] = mapped_column(Integer, default=0)
    longest_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="profile")

    # Override created_at from Base (no updated_at for this table)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class UserPreferences(Base):
    __tablename__ = "user_preferences"

    user_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE"), unique=True
    )
    language: Mapped[str] = mapped_column(String(10), default="zh-CN")
    font_size: Mapped[int] = mapped_column(SmallInteger, default=16)
    sound_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    theme: Mapped[str] = mapped_column(String(20), default="system")

    user: Mapped["User"] = relationship("User", back_populates="preferences")


class ParentLink(Base):
    __tablename__ = "parent_links"
    __table_args__ = (
        UniqueConstraint("parent_id", "student_id", name="uq_parent_student"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    parent_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE")
    )
    student_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE")
    )
    relation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notify_settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    parent: Mapped["User"] = relationship(
        "User", foreign_keys=[parent_id], back_populates="parent_links"
    )
    student: Mapped["User"] = relationship(
        "User", foreign_keys=[student_id], back_populates="student_links"
    )
