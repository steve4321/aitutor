from __future__ import annotations

# ruff: noqa: F821
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Float,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class KnowledgeState(Base):
    __tablename__ = "knowledge_states"
    __table_args__ = (
        UniqueConstraint(
            "student_id", "knowledge_point_id", name="uq_student_kp"
        ),
        Index("ix_ks_student_id", "student_id"),
        Index("ix_ks_knowledge_point_id", "knowledge_point_id"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    student_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE")
    )
    knowledge_point_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("knowledge_points.id", ondelete="CASCADE")
    )
    mastery: Mapped[float] = mapped_column(Float, default=0)
    mastery_level: Mapped[str] = mapped_column(String(20), default="not_started")
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    difficulty: Mapped[float] = mapped_column(Float, default=0)
    stability: Mapped[float] = mapped_column(Float, default=0)
    retrievability: Mapped[float] = mapped_column(Float, default=1.0)
    next_review: Mapped[datetime | None] = mapped_column(nullable=True)
    last_review: Mapped[datetime | None] = mapped_column(nullable=True)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    lapse_count: Mapped[int] = mapped_column(Integer, default=0)


class LearningSession(Base):
    __tablename__ = "learning_sessions"
    __table_args__ = (
        Index("ix_ls_student_id", "student_id"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    student_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE")
    )
    session_type: Mapped[str] = mapped_column(String(30), nullable=False)
    subject: Mapped[str] = mapped_column(String(20), nullable=False)
    knowledge_point_id: Mapped[UUID | None] = mapped_column(
        Uuid(), ForeignKey("knowledge_points.id", ondelete="SET NULL"), nullable=True
    )
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(nullable=True)
    duration_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    problems_total: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    problems_correct: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    score_pct: Mapped[float | None] = mapped_column(Float, nullable=True)
    xp_earned: Mapped[int] = mapped_column(Integer, default=0)
    checkpoint_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    attempts: Mapped[list["StudentAttempt"]] = relationship(
        "StudentAttempt", back_populates="session",
        cascade="all, delete-orphan",
    )
    messages: Mapped[list["Message"]] = relationship(
        "Message", back_populates="session",
        cascade="all, delete-orphan",
    )


class StudentAttempt(Base):
    __tablename__ = "student_attempts"
    __table_args__ = (
        Index("ix_sa_student_id", "student_id"),
        Index("ix_sa_session_id", "session_id"),
        Index("ix_sa_problem_id", "problem_id"),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    session_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("learning_sessions.id", ondelete="CASCADE")
    )
    student_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("users.id", ondelete="CASCADE")
    )
    problem_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("problems.id", ondelete="CASCADE")
    )
    answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_correct: Mapped[bool | None] = mapped_column(nullable=True)
    time_spent_sec: Mapped[int | None] = mapped_column(Integer, nullable=True)
    hint_level_used: Mapped[int] = mapped_column(SmallInteger, default=0)
    error_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)
    attempt_number: Mapped[int] = mapped_column(SmallInteger, default=1)

    session: Mapped["LearningSession"] = relationship(
        "LearningSession", back_populates="attempts"
    )
