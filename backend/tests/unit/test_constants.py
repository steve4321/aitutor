"""Unit tests for agent constants module."""

from app.agents.constants import MasteryConstants, SelectionConstants


class TestMasteryConstants:
    def test_increment_correct_is_positive(self):
        assert MasteryConstants.INCREMENT_CORRECT > 0

    def test_decrement_incorrect_is_positive(self):
        assert MasteryConstants.DECREMENT_INCORRECT > 0

    def test_increment_greater_than_decrement(self):
        assert MasteryConstants.INCREMENT_CORRECT > MasteryConstants.DECREMENT_INCORRECT

    def test_hint_penalty_per_level_is_positive(self):
        assert MasteryConstants.HINT_PENALTY_PER_LEVEL > 0

    def test_difficulty_bonus_multiplier_is_positive(self):
        assert MasteryConstants.DIFFICULTY_BONUS_MULTIPLIER > 0

    def test_difficulty_bonus_threshold_is_positive(self):
        assert MasteryConstants.DIFFICULTY_BONUS_THRESHOLD > 0

    def test_increment_correct_in_valid_range(self):
        assert 0 < MasteryConstants.INCREMENT_CORRECT <= 1.0

    def test_decrement_incorrect_in_valid_range(self):
        assert 0 < MasteryConstants.DECREMENT_INCORRECT <= 1.0

    def test_hint_penalty_is_small(self):
        assert MasteryConstants.HINT_PENALTY_PER_LEVEL < MasteryConstants.DECREMENT_INCORRECT


class TestSelectionConstants:
    def test_default_target_difficulty_in_range(self):
        assert 1 <= SelectionConstants.DEFAULT_TARGET_DIFFICULTY <= 10

    def test_recent_exclusion_days_positive(self):
        assert SelectionConstants.RECENT_PROBLEM_EXCLUSION_DAYS > 0

    def test_default_target_difficulty_non_zero(self):
        assert SelectionConstants.DEFAULT_TARGET_DIFFICULTY != 0

    def test_recent_exclusion_days_is_integer(self):
        assert isinstance(SelectionConstants.RECENT_PROBLEM_EXCLUSION_DAYS, int)
