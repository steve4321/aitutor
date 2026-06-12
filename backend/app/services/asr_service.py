"""Automatic Speech Recognition service using faster-whisper with OpenAI fallback."""
import asyncio
import logging
import os
import re
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy imports — packages may not be installed.
# ---------------------------------------------------------------------------
_faster_whisper = None
_faster_whisper_available: bool | None = None

# ---------------------------------------------------------------------------
# Math speech parser — Chinese math expressions → LaTeX / ASCII math
# ---------------------------------------------------------------------------
_MATH_PATTERNS: list[tuple[re.Pattern, str]] = [
    # Superscripts
    (re.compile(r"(\w)的?平方"), r"\1^2"),
    (re.compile(r"(\w)的?立方"), r"\1^3"),
    (re.compile(r"(\w)的?(\d+)次方"), r"\1^\2"),
    # Common operations
    (re.compile(r"加"), "+"),
    (re.compile(r"减"), "-"),
    (re.compile(r"乘以?"), "×"),
    (re.compile(r"除以?"), "÷"),
    (re.compile(r"等于"), "="),
    (re.compile(r"大于"), ">"),
    (re.compile(r"小于"), "<"),
    # Fractions
    (re.compile(r"(\d+)分之(\d+)"), r"\2/\1"),
    # Square root
    (re.compile(r"根号(\w)"), r"√\1"),
    (re.compile(r"开方"), "√"),
    # Parentheses
    (re.compile(r"左括号"), "("),
    (re.compile(r"右括号"), ")"),
    (re.compile(r"括号"), "()"),
    # Pi
    (re.compile(r"派"), "π"),
    (re.compile(r"圆周率"), "π"),
    # Absolute value
    (re.compile(r"绝对值"), "||"),
    # Percentage
    (re.compile(r"百分之(\d+)"), r"\1%"),
    # x / y variable normalization
    (re.compile(r"\b([a-zA-Z])\s*(\d)"), r"\1\2"),
]

# Numbers word → digit
_NUM_MAP = {
    "零": "0", "一": "1", "二": "2", "两": "2", "三": "3",
    "四": "4", "五": "5", "六": "6", "七": "7", "八": "8",
    "九": "9", "十": "10",
}


def parse_math_speech(text: str) -> str:
    """Convert spoken Chinese math to symbolic form.

    Examples::

        >>> parse_math_speech("x平方加5x加6")
        'x^2+5x+6'
        >>> parse_math_speech("x的平方减2x加1等于0")
        'x^2-2x+1=0'
    """
    if not text:
        return text

    result = text.strip()

    for word, digit in _NUM_MAP.items():
        result = result.replace(word, digit)

    for pattern, replacement in _MATH_PATTERNS:
        result = pattern.sub(replacement, result)

    result = re.sub(r"\s+", "", result)

    return result


def _is_faster_whisper_available() -> bool:
    global _faster_whisper_available, _faster_whisper
    if _faster_whisper_available is not None:
        return _faster_whisper_available
    try:
        from faster_whisper import WhisperModel  # type: ignore[import-untyped]
        _faster_whisper = WhisperModel
        _faster_whisper_available = True
    except ImportError:
        _faster_whisper_available = False
        logger.warning("faster-whisper is not installed — ASR features are disabled")
    return _faster_whisper_available


def _detect_mime_extension(content_type: str | None, filename: str | None) -> str:
    """Return a file extension (with dot) from MIME type or filename."""
    mime_map = {
        "audio/webm": ".webm",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/ogg": ".ogg",
        "audio/x-m4a": ".m4a",
        "audio/mp4": ".m4a",
        "audio/flac": ".flac",
    }
    if content_type and content_type in mime_map:
        return mime_map[content_type]
    if filename:
        ext = Path(filename).suffix.lower()
        if ext in (".webm", ".wav", ".mp3", ".ogg", ".m4a", ".flac"):
            return ext
    # Default to webm (browser MediaRecorder default)
    return ".webm"


async def transcribe_audio(
    audio_data: bytes,
    language: str = "zh",
    content_type: str | None = None,
    filename: str | None = None,
) -> dict:
    """Transcribe *audio_data* to text.

    Returns ``{"transcript": str, "language": str, "confidence": float}``.
    On failure returns a dict with an ``error`` key.
    """
    if not _is_faster_whisper_available():
        return await _transcribe_openai_fallback(audio_data, language, content_type, filename)

    ext = _detect_mime_extension(content_type, filename)
    tmp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp:
            tmp.write(audio_data)
            tmp_path = tmp.name

        result = await transcribe_file(tmp_path, language)
        return result
    except Exception:
        logger.exception("ASR transcription failed")
        return {"transcript": "", "language": language, "confidence": 0.0, "error": "Transcription failed"}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


async def transcribe_file(file_path: str, language: str = "zh") -> dict:
    """Transcribe an audio file to text using faster-whisper."""
    if not _is_faster_whisper_available():
        return await _transcribe_openai_fallback_file(file_path, language)

    try:
        WhisperModel = _faster_whisper
        model_size = os.environ.get("WHISPER_MODEL_SIZE", "base")
        model = WhisperModel(model_size, device="cpu", compute_type="int8")

        # faster-whisper is synchronous — run in thread pool
        loop = asyncio.get_running_loop()
        segments, info = await loop.run_in_executor(
            None,
            lambda: model.transcribe(file_path, language=language),
        )

        transcript_parts = []
        total_confidence = 0.0
        seg_count = 0
        for seg in segments:
            transcript_parts.append(seg.text.strip())
            total_confidence += seg.avg_logprob
            seg_count += 1

        transcript = " ".join(transcript_parts)
        # Convert avg_logprob to 0-1 confidence (rough heuristic)
        avg_logprob = total_confidence / max(seg_count, 1)
        confidence = max(0.0, min(1.0, (avg_logprob + 1.0)))  # logprob ∈ [-1, 0] typically

        return {
            "transcript": transcript,
            "language": info.language if hasattr(info, "language") else language,
            "confidence": round(confidence, 3),
        }
    except Exception:
        logger.exception("faster-whisper transcription failed")
        return {"transcript": "", "language": language, "confidence": 0.0, "error": "Transcription failed"}


async def score_pronunciation(
    audio_data: bytes,
    reference_text: str,
    language: str = "en",
    content_type: str | None = None,
    filename: str | None = None,
) -> dict:
    """Score pronunciation accuracy against *reference_text*.

    Returns::

        {
            "score": int,           # 0-100
            "confidence": float,    # 0.0-1.0
            "transcript": str,
            "word_scores": [...],   # per-word detail
        }
    """
    # First transcribe
    result = await transcribe_audio(audio_data, language, content_type, filename)
    transcript = result.get("transcript", "")
    confidence = result.get("confidence", 0.0)

    if not transcript:
        return {
            "score": 0,
            "confidence": 0.0,
            "transcript": "",
            "word_scores": [],
            "error": "Could not transcribe audio",
        }

    # Simple word-level scoring using edit distance
    word_scores = _compute_word_scores(transcript, reference_text)
    overall_score = _compute_overall_score(transcript, reference_text, confidence)

    return {
        "score": overall_score,
        "confidence": confidence,
        "transcript": transcript,
        "word_scores": word_scores,
    }


def _compute_word_scores(transcript: str, reference: str) -> list[dict]:
    """Compute per-word pronunciation scores via simple token matching."""
    ref_words = reference.lower().split()
    trans_words = transcript.lower().split()

    scores: list[dict] = []
    for i, ref_w in enumerate(ref_words):
        if i < len(trans_words):
            # Exact match → 100, partial → 50, else edit-distance based
            trans_w = trans_words[i]
            if trans_w == ref_w:
                score = 100
            elif ref_w in trans_w or trans_w in ref_w:
                score = 50
            else:
                # Levenshtein-based
                score = _simple_similarity(ref_w, trans_w)
            scores.append({"word": ref_w, "score": score, "heard": trans_w})
        else:
            scores.append({"word": ref_w, "score": 0, "heard": ""})

    return scores


def _simple_similarity(a: str, b: str) -> int:
    """Rough similarity score (0-100) between two short strings."""
    if not a or not b:
        return 0
    matches = sum(1 for ca, cb in zip(a, b) if ca == cb)
    ratio = matches / max(len(a), len(b))
    return int(ratio * 100)


def _compute_overall_score(transcript: str, reference: str, confidence: float) -> int:
    """Compute overall pronunciation score (0-100)."""
    ref_words = set(reference.lower().split())
    trans_words = set(transcript.lower().split())
    if not ref_words:
        return 0
    overlap = ref_words & trans_words
    word_accuracy = len(overlap) / len(ref_words)
    # Blend word accuracy with model confidence
    score = int(word_accuracy * 0.7 * 100 + confidence * 0.3 * 100)
    return min(max(score, 0), 100)


# ---------------------------------------------------------------------------
# OpenAI Whisper API fallback
# ---------------------------------------------------------------------------

async def _transcribe_openai_fallback(
    audio_data: bytes,
    language: str,
    content_type: str | None = None,
    filename: str | None = None,
) -> dict:
    """Attempt transcription using OpenAI Whisper API."""
    try:
        from openai import AsyncOpenAI

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return {"transcript": "", "language": language, "confidence": 0.0, "error": "ASR unavailable"}

        ext = _detect_mime_extension(content_type, filename)
        client = AsyncOpenAI()
        import io
        audio_file = io.BytesIO(audio_data)
        audio_file.name = f"audio{ext}"

        response = await client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,  # type: ignore[arg-type]
            language=language,
            response_format="verbose_json",
        )
        transcript = response.text if hasattr(response, "text") else str(response)
        return {
            "transcript": transcript,
            "language": language,
            "confidence": 0.9,  # OpenAI doesn't expose confidence
        }
    except Exception:
        logger.exception("OpenAI Whisper API fallback failed")
        return {"transcript": "", "language": language, "confidence": 0.0, "error": "ASR unavailable"}


async def _transcribe_openai_fallback_file(file_path: str, language: str) -> dict:
    """Fallback using OpenAI Whisper API from a file path."""
    try:
        with open(file_path, "rb") as f:
            audio_data = f.read()
        ext = Path(file_path).suffix
        return await _transcribe_openai_fallback(audio_data, language, filename=f"audio{ext}")
    except Exception:
        logger.exception("OpenAI Whisper API file fallback failed")
        return {"transcript": "", "language": language, "confidence": 0.0, "error": "ASR unavailable"}
