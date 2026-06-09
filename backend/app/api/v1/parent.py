from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select

from app.api.deps import DbSession, get_current_user
from app.models.user import ParentLink, User
from app.schemas.report import WeeklyReport
from app.schemas.user import ParentLinkRequest, ParentLinkResponse
from app.services import report_service

router = APIRouter(prefix="/parent", tags=["parent"])


@router.post("/link", response_model=ParentLinkResponse)
async def create_parent_link(
    body: ParentLinkRequest,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    """Link student to parent via 6-digit code derived from parent UUID hex prefix."""
    link_code = body.link_code.strip()
    if len(link_code) != 6 or not link_code.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid link code: must be exactly 6 digits",
        )

    parents_result = await db.execute(
        select(User).where(User.role == "parent")
    )
    parents = parents_result.scalars().all()

    matched_parent = None
    for parent in parents:
        parent_code = str(parent.id).replace("-", "")[:6]
        try:
            numeric_code = str(int(parent_code, 16) % 1000000).zfill(6)
        except ValueError:
            continue
        if numeric_code == link_code:
            matched_parent = parent
            break

    if matched_parent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No parent found with this link code",
        )

    existing = await db.execute(
        select(ParentLink).where(
            and_(
                ParentLink.parent_id == matched_parent.id,
                ParentLink.student_id == current_user.id,
            )
        )
    )
    if existing.scalar_one_or_none() is not None:
        return ParentLinkResponse(
            status="already_linked",
            parent_name=matched_parent.name,
        )

    link = ParentLink(
        parent_id=matched_parent.id,
        student_id=current_user.id,
        relation=None,
    )
    db.add(link)
    await db.commit()

    return ParentLinkResponse(
        status="linked",
        parent_name=matched_parent.name,
    )


@router.get("/children/{student_id}/report", response_model=WeeklyReport)
async def get_child_report(
    student_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    link_result = await db.execute(
        select(ParentLink).where(
            and_(
                ParentLink.parent_id == current_user.id,
                ParentLink.student_id == student_id,
            )
        )
    )
    if link_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this student's report",
        )

    target_start = date.today() - timedelta(days=date.today().weekday())
    target_end = target_start + timedelta(days=7)
    dt_start = datetime.combine(target_start, datetime.min.time())
    dt_end = datetime.combine(target_end, datetime.min.time())

    agg = await report_service.aggregate_sessions(db, student_id, dt_start, dt_end)
    streak_days = await report_service.get_streak_days(db, student_id)

    return WeeklyReport(
        week_start=target_start,
        week_end=target_end - timedelta(days=1),
        total_sessions=agg["total_sessions"],
        total_problems=agg["total_problems"],
        total_correct=agg["total_correct"],
        total_xp=agg["total_xp"],
        total_time_minutes=agg["total_time_minutes"],
        streak_days=streak_days,
        mastery_changes={},
    )
