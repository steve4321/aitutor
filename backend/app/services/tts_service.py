"""Text-to-Speech service using Edge TTS with audio caching."""
import hashlib
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

_edge_tts = None
_edge_tts_available: bool | None = None

SUPPORTED_VOICES: dict[str, dict[str, str]] = {
    "zh-CN-XiaoxiaoNeural": {"lang": "zh-CN", "gender": "Female", "label": "晓晓 (女)"},
    "zh-CN-XiaoyiNeural": {"lang": "zh-CN", "gender": "Female", "label": "晓依 (女)"},
    "zh-CN-YunjianNeural": {"lang": "zh-CN", "gender": "Male", "label": "云健 (男)"},
    "zh-CN-YunxiNeural": {"lang": "zh-CN", "gender": "Male", "label": "云希 (男)"},
    "zh-CN-YunxiaNeural": {"lang": "zh-CN", "gender": "Male", "label": "云霞 (男)"},
    "zh-CN-YunyangNeural": {"lang": "zh-CN", "gender": "Male", "label": "云扬 (男)"},
    "en-US-JennyNeural": {"lang": "en-US", "gender": "Female", "label": "Jenny (F)"},
    "en-US-GuyNeural": {"lang": "en-US", "gender": "Male", "label": "Guy (M)"},
    "en-US-AriaNeural": {"lang": "en-US", "gender": "Female", "label": "Aria (F)"},
    "en-US-DavisNeural": {"lang": "en-US", "gender": "Male", "label": "Davis (M)"},
}

_CACHE_DIR = Path(tempfile.gettempdir()) / "aitutor_tts_cache"


def _ensure_cache_dir() -> Path:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return _CACHE_DIR


def _cache_key(text: str, voice: str, rate: str) -> str:
    raw = f"{text}|{voice}|{rate}"
    return hashlib.sha256(raw.encode()).hexdigest() + ".mp3"


def _is_available() -> bool:
    global _edge_tts_available, _edge_tts
    if _edge_tts_available is not None:
        return _edge_tts_available
    try:
        import edge_tts as _et  # type: ignore[import-untyped]
        _edge_tts = _et
        _edge_tts_available = True
    except ImportError:
        _edge_tts_available = False
        logger.warning("edge-tts is not installed — TTS features are disabled")
    return _edge_tts_available


async def text_to_speech(
    text: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str = "+0%",
) -> bytes | None:
    if not _is_available():
        logger.warning("edge-tts unavailable — cannot generate speech")
        return None

    cache_path = _ensure_cache_dir() / _cache_key(text, voice, rate)
    if cache_path.exists():
        logger.debug("TTS cache hit: %s", cache_path.name)
        return cache_path.read_bytes()

    try:
        communicate = _edge_tts.Communicate(text, voice, rate=rate)  # type: ignore[union-attr]
        import io
        buffer = io.BytesIO()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                buffer.write(chunk["data"])
        audio_bytes = buffer.getvalue()
        if audio_bytes:
            cache_path.write_bytes(audio_bytes)
        return audio_bytes or None
    except Exception:
        logger.exception("Edge TTS synthesis failed")
        return None


async def save_tts_audio(
    text: str,
    output_path: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
    rate: str = "+0%",
) -> str | None:
    audio = await text_to_speech(text, voice, rate)
    if audio is None:
        return None
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_path).write_bytes(audio)
    return output_path


def get_available_voices() -> list[dict[str, str]]:
    return [
        {"id": vid, **meta}
        for vid, meta in SUPPORTED_VOICES.items()
    ]
