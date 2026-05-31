"""Unit tests for prompt template registry."""
import pytest

from app.agents.prompts import get_system_prompt, list_prompts

EXPECTED_PROMPTS = [
    "math_socratic",
    "math_course",
    "ket_writing",
    "error_diagnosis",
    "chn_writing",
    "poetry_teaching",
    "poetry_dictation",
    "poetry_scoring",
]


class TestPromptRegistry:
    def test_all_prompts_registered(self):
        for key in EXPECTED_PROMPTS:
            result = get_system_prompt(key)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_list_prompts_returns_all(self):
        keys = list_prompts()
        assert len(keys) == 8
        for key in EXPECTED_PROMPTS:
            assert key in keys

    def test_unknown_prompt_raises_key_error(self):
        with pytest.raises(KeyError, match="Unknown prompt"):
            get_system_prompt("nonexistent_prompt")


class TestMathSocraticRendering:
    ALL_VARS = {
        "student_name": "小明",
        "grade_level": "5",
        "target_exam": "AMC8",
        "mastery_level": "familiar",
        "mastered_kps": "algebra.01",
        "weak_areas": "geometry",
        "problem_markdown": "2x + 3 = 7",
        "correct_answer": "x=2",
        "reference_solutions": "两边减3再除以2",
        "hint_level": "1",
    }

    def test_renders_all_vars(self):
        result = get_system_prompt("math_socratic", **self.ALL_VARS)
        for var_name in self.ALL_VARS:
            assert "{" + var_name + "}" not in result

    def test_contains_student_name(self):
        result = get_system_prompt("math_socratic", **self.ALL_VARS)
        assert "小明" in result


class TestErrorDiagnosisRendering:
    def test_renders_with_all_vars(self):
        result = get_system_prompt(
            "error_diagnosis",
            problem="2x + 3 = 7",
            student_answer="x=5",
            correct_answer="x=2",
            student_work="2x = 7, x = 7/2",
        )
        assert "x=5" in result
        assert "x=2" in result

    def test_missing_variable_no_error(self):
        result = get_system_prompt("error_diagnosis", problem="2x+3=7")
        assert isinstance(result, str)


class TestDoubleBraces:
    def test_json_double_braces_become_single(self):
        result = get_system_prompt(
            "error_diagnosis",
            problem="p",
            student_answer="a",
            correct_answer="c",
            student_work="w",
        )
        assert '"error_type"' in result
        assert '{{' not in result
