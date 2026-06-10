"""Unit tests for the FSRS spaced-repetition algorithm."""

import pytest

from app.agents.services.fsrs import (
    DEFAULT_PARAMS,
    calculate_retrievability,
    classify_mastery_level,
    initial_difficulty,
    initial_stability,
    rating_from_correctness,
    update_difficulty,
    update_stability,
)


class TestInitialValues:
    def test_initial_stability_rating_1(self):
        assert initial_stability(1) == pytest.approx(DEFAULT_PARAMS.w[0])

    def test_initial_stability_rating_2(self):
        assert initial_stability(2) == pytest.approx(DEFAULT_PARAMS.w[1])

    def test_initial_stability_rating_3(self):
        assert initial_stability(3) == pytest.approx(DEFAULT_PARAMS.w[2])

    def test_initial_stability_rating_4(self):
        assert initial_stability(4) == pytest.approx(DEFAULT_PARAMS.w[3])

    def test_initial_stability_clamped_below_1(self):
        assert initial_stability(0) == pytest.approx(DEFAULT_PARAMS.w[0])

    def test_initial_stability_clamped_above_4(self):
        assert initial_stability(99) == pytest.approx(DEFAULT_PARAMS.w[3])

    def test_initial_difficulty_in_range(self):
        for rating in range(1, 5):
            d = initial_difficulty(rating)
            assert 1.0 <= d <= 10.0

    def test_initial_difficulty_decreases_with_rating(self):
        d1 = initial_difficulty(1)
        d2 = initial_difficulty(2)
        d3 = initial_difficulty(3)
        d4 = initial_difficulty(4)
        assert d1 > d2  # Higher rating = lower difficulty
        assert d2 > d3  # Still decreasing
        assert d3 >= d4  # May clamp to same value


class TestUpdateFunctions:
    def test_update_stability_rating_1_halves(self):
        s = 10.0
        new_s = update_stability(difficulty=5.0, stability=s, rating=1)
        assert new_s == pytest.approx(max(0.1, s * 0.5))

    def test_update_stability_rating_4_increases(self):
        s = 10.0
        new_s = update_stability(difficulty=5.0, stability=s, rating=4)
        assert new_s > s

    def test_update_stability_zero_stability_fallback(self):
        new_s = update_stability(difficulty=5.0, stability=0.0, rating=4)
        assert new_s == pytest.approx(initial_stability(4))

    def test_update_stability_negative_stability_fallback(self):
        new_s = update_stability(difficulty=5.0, stability=-1.0, rating=3)
        assert new_s == pytest.approx(initial_stability(3))

    def test_update_stability_rating_1_minimum_0_1(self):
        new_s = update_stability(difficulty=5.0, stability=0.1, rating=1)
        assert new_s >= 0.1

    def test_update_stability_capped_at_365(self):
        new_s = update_stability(difficulty=1.0, stability=400.0, rating=4)
        assert new_s <= 365.0

    def test_update_difficulty_converges_to_mean(self):
        d = 1.0
        for _ in range(100):
            d = update_difficulty(d, rating=3)
        mean_d = initial_difficulty(3)
        assert d == pytest.approx(mean_d, abs=0.1)

    def test_update_difficulty_stays_in_range(self):
        d = 1.0
        for rating in [1, 4, 2, 3, 1, 4]:
            d = update_difficulty(d, rating)
        assert 1.0 <= d <= 10.0


class TestRetrievability:
    def test_zero_days_returns_near_one(self):
        r = calculate_retrievability(stability=10.0, elapsed_days=0.0)
        assert r == pytest.approx(1.0)

    def test_decreases_over_time(self):
        r0 = calculate_retrievability(stability=10.0, elapsed_days=1.0)
        r5 = calculate_retrievability(stability=10.0, elapsed_days=5.0)
        r10 = calculate_retrievability(stability=10.0, elapsed_days=10.0)
        assert r0 > r5 > r10

    def test_zero_stability_returns_zero(self):
        r = calculate_retrievability(stability=0.0, elapsed_days=5.0)
        assert r == 0.0

    def test_negative_stability_returns_zero(self):
        r = calculate_retrievability(stability=-1.0, elapsed_days=5.0)
        assert r == 0.0

    def test_high_stability_stays_high(self):
        r = calculate_retrievability(stability=100.0, elapsed_days=1.0)
        assert r > 0.9


class TestMasteryClassification:
    @pytest.mark.parametrize(
        "mastery, expected",
        [
            (0.0, "not_started"),
            (0.05, "not_started"),
            (0.09, "not_started"),
            (0.1, "attempted"),
            (0.2, "attempted"),
            (0.29, "attempted"),
            (0.3, "familiar"),
            (0.45, "familiar"),
            (0.59, "familiar"),
            (0.6, "proficient"),
            (0.7, "proficient"),
            (0.84, "proficient"),
            (0.85, "mastered"),
            (0.95, "mastered"),
            (1.0, "mastered"),
        ],
    )
    def test_classify(self, mastery, expected):
        assert classify_mastery_level(mastery) == expected


class TestRatingMapping:
    def test_wrong_maps_to_1(self):
        assert rating_from_correctness(is_correct=False) == 1

    def test_correct_no_hint_maps_to_4(self):
        assert rating_from_correctness(is_correct=True, hint_level=0) == 4

    def test_correct_one_hint_maps_to_3(self):
        assert rating_from_correctness(is_correct=True, hint_level=1) == 3

    def test_correct_two_hints_maps_to_3(self):
        assert rating_from_correctness(is_correct=True, hint_level=2) == 3

    def test_correct_three_hints_maps_to_2(self):
        assert rating_from_correctness(is_correct=True, hint_level=3) == 2

    def test_correct_four_hints_maps_to_2(self):
        assert rating_from_correctness(is_correct=True, hint_level=4) == 2
