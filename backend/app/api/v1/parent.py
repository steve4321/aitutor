from datetime import date, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import DbSession, get_current_user
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models.knowledge import KnowledgePoint
from app.models.learning import KnowledgeState
from app.models.user import ParentLink, StudentProfile, User
from app.schemas.parent import (
    ChildOverview,
    LinkedChild,
    MasteryTrendsResponse,
    MasteryTrend,
    NotificationsResponse,
    PillarMasteryValues,
)
from app.schemas.report import WeeklyReport
from app.schemas.user import ParentLinkRequest, ParentLinkResponse
from app.services import report_service

router = APIRouter(prefix="/parent", tags=["parent"])

PILLAR_KEY_MAP = {
    "Algebra": "algebra",
    "Geometry": "geometry",
    "Counting & Probability": "counting",
    "Number Theory": "number_theory",
}


async def _verify_parent_access(
    db: AsyncSession, parent_id: UUID, student_id: UUID
) -> None:
    link_result = await db.execute(
        select(ParentLink).where(
            and_(
                ParentLink.parent_id == parent_id,
                ParentLink.student_id == student_id,
            )
        )
    )
    if link_result.scalar_one_or_none() is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this student's data",
        )


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


@router.get("/children", response_model=list[LinkedChild])
@limiter.limit(RATE_LIMITS["api_read"])
async def list_children(
    request: Request,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "parent":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parent accounts can access this endpoint",
        )

    result = await db.execute(
        select(User, StudentProfile, ParentLink)
        .join(User, ParentLink.student_id == User.id)
        .outerjoin(StudentProfile, StudentProfile.user_id == User.id)
        .where(ParentLink.parent_id == current_user.id)
    )

    children: list[LinkedChild] = []
    for student, profile, link in result.all():
        children.append(
            LinkedChild(
                id=student.id,
                name=student.name,
                grade_level=profile.grade_level if profile else None,
                target_exam=profile.target_exam if profile else None,
                streak_days=profile.streak_days if profile else 0,
                xp_total=profile.xp_total if profile else 0,
                linked_at=link.created_at,
            )
        )
    return children


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
    mastery_changes = await report_service.get_mastery_changes(
        db, student_id, dt_start, dt_end
    )

    return WeeklyReport(
        week_start=target_start,
        week_end=target_end - timedelta(days=1),
        total_sessions=agg["total_sessions"],
        total_problems=agg["total_problems"],
        total_correct=agg["total_correct"],
        total_xp=agg["total_xp"],
        total_time_minutes=agg["total_time_minutes"],
        streak_days=streak_days,
        mastery_changes=mastery_changes,
    )


@router.get("/children/{student_id}/overview", response_model=ChildOverview)
@limiter.limit(RATE_LIMITS["api_read"])
async def get_child_overview(
    request: Request,
    student_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    await _verify_parent_access(db, current_user.id, student_id)

    profile_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id == student_id)
    )
    profile = profile_result.scalar_one_or_none()

    student_result = await db.execute(
        select(User).where(User.id == student_id)
    )
    student = student_result.scalar_one_or_none()

    streak_days = profile.streak_days if profile else 0
    target_exam = profile.target_exam if profile else None
    daily_goal_minutes = profile.daily_goal_minutes if profile else 20

    today = date.today()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=7)
    week_agg = await report_service.aggregate_sessions(
        db,
        student_id,
        datetime.combine(week_start, datetime.min.time()),
        datetime.combine(week_end, datetime.min.time()),
    )
    weekly_study_minutes = week_agg["total_time_minutes"]

    today_agg = await report_service.aggregate_sessions(
        db,
        student_id,
        datetime.combine(today, datetime.min.time()),
        datetime.combine(today + timedelta(days=1), datetime.min.time()),
    )
    minutes_today = today_agg["total_time_minutes"]

    weekly_goal = daily_goal_minutes * 7
    if weekly_goal > 0:
        weekly_goal_completion = min(
            100, round(weekly_study_minutes / weekly_goal * 100)
        )
    else:
        weekly_goal_completion = 0

    return ChildOverview(
        child_id=student_id,
        child_name=student.name if student else "",
        target_exam=target_exam,
        streak_days=streak_days,
        weekly_study_minutes=weekly_study_minutes,
        weekly_goal_completion=weekly_goal_completion,
        minutes_today=minutes_today,
        daily_goal_minutes=daily_goal_minutes,
    )


@router.get("/children/{student_id}/mastery", response_model=MasteryTrendsResponse)
@limiter.limit(RATE_LIMITS["api_read"])
async def get_child_mastery(
    request: Request,
    student_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    await _verify_parent_access(db, current_user.id, student_id)

    today = date.today()
    current_monday = today - timedelta(days=today.weekday())

    trends: list[MasteryTrend] = []
    for i in range(4):
        week_start = current_monday - timedelta(weeks=3 - i)
        week_end = week_start + timedelta(days=7)
        dt_start = datetime.combine(week_start, datetime.min.time())
        dt_end = datetime.combine(week_end, datetime.min.time())

        result = await db.execute(
            select(KnowledgePoint.pillar, func.avg(KnowledgeState.mastery))
            .join(
                KnowledgePoint,
                KnowledgeState.knowledge_point_id == KnowledgePoint.id,
            )
            .where(
                and_(
                    KnowledgeState.student_id == student_id,
                    KnowledgePoint.pillar.isnot(None),
                    KnowledgeState.last_review >= dt_start,
                    KnowledgeState.last_review < dt_end,
                )
            )
            .group_by(KnowledgePoint.pillar)
        )

        pillar_values = {
            "algebra": 0.0,
            "geometry": 0.0,
            "counting": 0.0,
            "number_theory": 0.0,
        }
        for pillar_name, avg_mastery in result.all():
            key = PILLAR_KEY_MAP.get(pillar_name)
            if key:
                pillar_values[key] = round(float(avg_mastery) * 100, 1)

        trends.append(
            MasteryTrend(
                week_start=week_start,
                pillars=PillarMasteryValues(**pillar_values),
            )
        )

    return MasteryTrendsResponse(child_id=student_id, trends=trends)


@router.get(
    "/children/{student_id}/notifications", response_model=NotificationsResponse
)
@limiter.limit(RATE_LIMITS["api_read"])
async def get_child_notifications(
    request: Request,
    student_id: UUID,
    db: DbSession,
    current_user: User = Depends(get_current_user),
):
    await _verify_parent_access(db, current_user.id, student_id)

    # TODO: query from a notifications table once it exists
    return NotificationsResponse(items=[], total=0)
