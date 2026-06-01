from __future__ import annotations

# ruff: noqa: F821
from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy import JSON as JSONB, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[UUID] = mapped_column(
        Uuid(), primary_key=True, default=uuid4
    )
    session_id: Mapped[UUID] = mapped_column(
        Uuid(), ForeignKey("learning_sessions.id", ondelete="CASCADE")
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    media: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    session: Mapped["LearningSession"] = relationship(
        "LearningSession", back_populates="messages"
    )
