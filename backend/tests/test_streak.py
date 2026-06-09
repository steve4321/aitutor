import pytest
from datetime import date, timedelta

from app.services.xp_service import update_streak, award_lesson_xp
from app.models.user import User, StudentProfile


@pytest.fixture
def _make_user_and_profile():
    from app.core.security import hash_password

    async def _factory(db_session, *, streak_days=0, longest_streak=0,
                       last_active_date=None, xp_total=0, name_suffix="1"):
        user = User(
            name=f"streak_user_{name_suffix}",
            password_hash=hash_password("pass1234"),
            role="student",
        )
        db_session.add(user)
        await db_session.flush()
        profile = StudentProfile(
            user_id=user.id,
            streak_days=streak_days,
            longest_streak=longest_streak,
            last_active_date=last_active_date,
            xp_total=xp_total,
        )
        db_session.add(profile)
        await db_session.flush()
        return user, profile

    return _factory


@pytest.mark.asyncio
async def test_streak_first_activity(db_session, _make_user_and_profile):
    _, profile = await _make_user_and_profile(db_session, name_suffix="first")
    new_streak = await update_streak(db_session, profile.user_id, profile=profile)
    assert new_streak == 1
    assert profile.streak_days == 1
    assert profile.last_active_date == date.today()


@pytest.mark.asyncio
async def test_streak_continues(db_session, _make_user_and_profile):
    _, profile = await _make_user_and_profile(
        db_session,
        streak_days=5,
        longest_streak=5,
        last_active_date=date.today() - timedelta(days=1),
        name_suffix="cont",
    )
    new_streak = await update_streak(db_session, profile.user_id, profile=profile)
    assert new_streak == 6
    assert profile.longest_streak == 6


@pytest.mark.asyncio
async def test_streak_breaks(db_session, _make_user_and_profile):
    _, profile = await _make_user_and_profile(
        db_session,
        streak_days=10,
        longest_streak=10,
        last_active_date=date.today() - timedelta(days=5),
        name_suffix="break",
    )
    new_streak = await update_streak(db_session, profile.user_id, profile=profile)
    assert new_streak == 1
    assert profile.longest_streak == 10


@pytest.mark.asyncio
async def test_streak_same_day_no_change(db_session, _make_user_and_profile):
    _, profile = await _make_user_and_profile(
        db_session,
        streak_days=7,
        last_active_date=date.today(),
        name_suffix="same",
    )
    new_streak = await update_streak(db_session, profile.user_id, profile=profile)
    assert new_streak == 7


@pytest.mark.asyncio
async def test_award_lesson_xp_updates_streak(db_session, _make_user_and_profile):
    _, profile = await _make_user_and_profile(
        db_session,
        xp_total=100,
        streak_days=0,
        name_suffix="lesson",
    )
    xp = await award_lesson_xp(db_session, profile.user_id)
    assert xp == 50
    assert profile.xp_total == 150
    assert profile.streak_days == 1
