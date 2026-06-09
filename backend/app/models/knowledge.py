from uuid import UUID, uuid4

from sqlalchemy import (
    ForeignKey,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, EmbeddingType


class KnowledgePoint(Base):
    __tablename__ = "knowledge_points"

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    subject: Mapped[str] = mapped_column(String(20), nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_en: Mapped[str | None] = mapped_column(String(200), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    pillar: Mapped[str | None] = mapped_column(String(50), nullable=True)
    difficulty_level: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    amc_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=8)
    lesson_id: Mapped[UUID | None] = mapped_column(
        Uuid(), ForeignKey("lessons.id", ondelete="SET NULL", use_alter=True), nullable=True
    )
    sort_order: Mapped[int | None] = mapped_column(SmallInteger, nullable=True)
    estimated_minutes: Mapped[int | None] = mapped_column(
        SmallInteger, nullable=True
    )
    amc_levels: Mapped[str | None] = mapped_column(String(50), nullable=True)
    embedding: Mapped[str | None] = mapped_column(EmbeddingType, nullable=True)

    prerequisites: Mapped[list["KnowledgeDependency"]] = relationship(
        "KnowledgeDependency",
        foreign_keys="KnowledgeDependency.target_id",
        back_populates="target",
        cascade="all, delete-orphan",
    )
    dependents: Mapped[list["KnowledgeDependency"]] = relationship(
        "KnowledgeDependency",
        foreign_keys="KnowledgeDependency.prerequisite_id",
        back_populates="prerequisite",
        cascade="all, delete-orphan",
    )


class KnowledgeDependency(Base):
    __tablename__ = "knowledge_dependencies"
    __table_args__ = (
        UniqueConstraint(
            "prerequisite_id", "target_id", name="uq_prerequisite_target"
        ),
    )

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    prerequisite_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("knowledge_points.id", ondelete="CASCADE")
    )
    target_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("knowledge_points.id", ondelete="CASCADE")
    )
    dependency_type: Mapped[str] = mapped_column(
        String(20), default="requires"
    )
    strength: Mapped[int] = mapped_column(SmallInteger, default=1)

    prerequisite: Mapped["KnowledgePoint"] = relationship(
        "KnowledgePoint", foreign_keys=[prerequisite_id], back_populates="dependents"
    )
    target: Mapped["KnowledgePoint"] = relationship(
        "KnowledgePoint", foreign_keys=[target_id], back_populates="prerequisites"
    )
