from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, SmallInteger, String, Text
from sqlalchemy import JSON as JSONB, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Problem(Base):
    __tablename__ = "problems"

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_year: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    source_code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    subject: Mapped[str] = mapped_column(String(20), nullable=False)
    format: Mapped[str] = mapped_column(String(30), nullable=False)
    question_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    question_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    options: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    correct_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    knowledge_point_ids: Mapped[dict | None] = mapped_column(
        JSONB, nullable=True
    )
    difficulty: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    estimated_time_sec: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    hints: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    misconceptions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    step_decomposition: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    times_attempted: Mapped[int] = mapped_column(Integer, default=0)
    times_correct: Mapped[int] = mapped_column(Integer, default=0)
    avg_time_sec: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    # pgvector Vector(1536) in production; TEXT placeholder for dev scaffolding
    embedding: Mapped[str | None] = mapped_column(Text, nullable=True)

    solutions: Mapped[list["ProblemSolution"]] = relationship(
        "ProblemSolution", back_populates="problem"
    )


class ProblemSolution(Base):
    __tablename__ = "problem_solutions"

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    problem_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("problems.id")
    )
    method_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    solution_markdown: Mapped[str] = mapped_column(Text, nullable=False)
    key_insight: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)

    problem: Mapped["Problem"] = relationship("Problem", back_populates="solutions")
