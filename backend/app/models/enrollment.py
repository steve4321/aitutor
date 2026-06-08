from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Index, SmallInteger, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Enrollment(Base):
    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),
        Index("ix_enrollments_user_active", "user_id", "is_active"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("users.id"))
    course_id: Mapped[UUID] = mapped_column(Uuid(), ForeignKey("courses.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    progress: Mapped[int] = mapped_column(SmallInteger, default=0)
