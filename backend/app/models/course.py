from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, SmallInteger, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Course(Base):
    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    code: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    subject: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    target_exam: Mapped[str | None] = mapped_column(String(50), nullable=True)
    estimated_hours: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    units: Mapped[list["Unit"]] = relationship("Unit", back_populates="course")


class Unit(Base):
    __tablename__ = "units"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    course_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("courses.id")
    )
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    required_mastery: Mapped[float] = mapped_column(default=0.8)

    course: Mapped["Course"] = relationship("Course", back_populates="units")
    lessons: Mapped[list["Lesson"]] = relationship("Lesson", back_populates="unit")


class Lesson(Base):
    __tablename__ = "lessons"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    unit_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("units.id")
    )
    knowledge_point_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("knowledge_points.id"), nullable=True
    )
    code: Mapped[str | None] = mapped_column(String(50), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    lesson_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    content: Mapped[dict] = mapped_column(JSONB, nullable=False)
    estimated_minutes: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    sort_order: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)

    unit: Mapped["Unit"] = relationship("Unit", back_populates="lessons")
