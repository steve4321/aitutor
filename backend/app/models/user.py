from datetime import date, datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    __tablename__ = "users"

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
        "StudentProfile", back_populates="user", uselist=False
    )
    parent_links: Mapped[list["ParentLink"]] = relationship(
        "ParentLink", foreign_keys="ParentLink.parent_id", back_populates="parent"
    )
    student_links: Mapped[list["ParentLink"]] = relationship(
        "ParentLink", foreign_keys="ParentLink.student_id", back_populates="student"
    )


class StudentProfile(Base):
    __tablename__ = "student_profiles"
    __table_args__ = ({"extend_existing": True},)

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), unique=True
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
        default=lambda: datetime.now(), nullable=False
    )


class ParentLink(Base):
    __tablename__ = "parent_links"
    __table_args__ = (
        UniqueConstraint("parent_id", "student_id", name="uq_parent_student"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    parent_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    student_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    relation: Mapped[str | None] = mapped_column(String(20), nullable=True)
    notify_settings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    parent: Mapped["User"] = relationship(
        "User", foreign_keys=[parent_id], back_populates="parent_links"
    )
    student: Mapped["User"] = relationship(
        "User", foreign_keys=[student_id], back_populates="student_links"
    )
