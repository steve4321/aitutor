from uuid import uuid4

from sqlalchemy import Integer, String, Text
from sqlalchemy import JSON as JSONB, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class KETQuestion(Base):
    __tablename__ = "ket_questions"

    id: Mapped[str] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    skill: Mapped[str] = mapped_column(String(20), nullable=False)
    level: Mapped[str] = mapped_column(String(10), nullable=False, default="A2")
    question_type: Mapped[str] = mapped_column(String(30), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    audio_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str] = mapped_column(Text, nullable=False)
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    points: Mapped[int] = mapped_column(Integer, default=1)


class KETWritingTask(Base):
    __tablename__ = "ket_writing_tasks"

    id: Mapped[str] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    task_type: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    word_limit_min: Mapped[int] = mapped_column(Integer, default=25)
    word_limit_max: Mapped[int] = mapped_column(Integer, default=50)
    sample_response: Mapped[str | None] = mapped_column(Text, nullable=True)


class KETSpeakingTask(Base):
    __tablename__ = "ket_speaking_tasks"

    id: Mapped[str] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    topic: Mapped[str] = mapped_column(String(100), nullable=False)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="easy")
    expected_duration_sec: Mapped[int] = mapped_column(Integer, default=30)
