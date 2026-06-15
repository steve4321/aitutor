"""Prompt template registry."""
import logging

from app.agents.prompts.math_socratic import MATH_SOCRATIC_TEMPLATE
from app.agents.prompts.math_course import MATH_COURSE_TEMPLATE
from app.agents.prompts.ket_writing import KET_WRITING_TEMPLATE
from app.agents.prompts.error_diagnosis import ERROR_DIAGNOSIS_TEMPLATE
from app.agents.prompts.chn_writing import CHN_WRITING_TEMPLATE
from app.agents.prompts.poetry_teaching import POETRY_TEACHING_TEMPLATE
from app.agents.prompts.poetry_dictation import POETRY_DICTATION_TEMPLATE
from app.agents.prompts.poetry_scoring import POETRY_SCORING_TEMPLATE
from app.agents.prompts.curriculum_recommendation import (
    CURRICULUM_SESSION_INIT_TEMPLATE,
    CURRICULUM_PROGRESS_TEMPLATE,
)
from app.agents.prompts.ket_speaking import KET_SPEAKING_TEMPLATE
from app.agents.prompts.chn_poetry_practice import CHN_POETRY_PRACTICE_TEMPLATE
from app.agents.prompts.amc_math_review import AMC_MATH_REVIEW_TEMPLATE
from app.agents.prompts.amc_math_diagnostic import AMC_MATH_DIAGNOSTIC_TEMPLATE
from app.agents.prompts.session_summary import SESSION_SUMMARY_TEMPLATE

logger = logging.getLogger(__name__)

_PROMPTS = {
    "math_socratic": MATH_SOCRATIC_TEMPLATE,
    "math_course": MATH_COURSE_TEMPLATE,
    "ket_writing": KET_WRITING_TEMPLATE,
    "error_diagnosis": ERROR_DIAGNOSIS_TEMPLATE,
    "chn_writing": CHN_WRITING_TEMPLATE,
    "poetry_teaching": POETRY_TEACHING_TEMPLATE,
    "poetry_dictation": POETRY_DICTATION_TEMPLATE,
    "poetry_scoring": POETRY_SCORING_TEMPLATE,
    "curriculum_session_init": CURRICULUM_SESSION_INIT_TEMPLATE,
    "curriculum_progress": CURRICULUM_PROGRESS_TEMPLATE,
    "ket_speaking": KET_SPEAKING_TEMPLATE,
    "chn_poetry_practice": CHN_POETRY_PRACTICE_TEMPLATE,
    "amc_math_review": AMC_MATH_REVIEW_TEMPLATE,
    "amc_math_diagnostic": AMC_MATH_DIAGNOSTIC_TEMPLATE,
    "session_summary": SESSION_SUMMARY_TEMPLATE,
}


class _SafeDict(dict):
    def __missing__(self, key):
        logger.warning(f"Missing prompt variable: {key}")
        return f"{{{{{key}}}}}"


def get_system_prompt(prompt_key: str, **kwargs) -> str:
    """
    Get a rendered system prompt.
    Uses str.format_map with safe missing-key handling.
    """
    template = _PROMPTS.get(prompt_key)
    if template is None:
        raise KeyError(f"Unknown prompt: {prompt_key}")
    return template.format_map(_SafeDict(**kwargs))


def list_prompts() -> list[str]:
    return list(_PROMPTS.keys())
