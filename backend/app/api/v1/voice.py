from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.core.rate_limit import RATE_LIMITS, limiter
from app.models.user import User
from app.services import tts_service, asr_service

router = APIRouter(prefix="/voice", tags=["voice"])


class TTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    voice: str = "zh-CN-XiaoxiaoNeural"
    rate: str = "+0%"


class PronunciationRequest(BaseModel):
    reference_text: str = Field(..., min_length=1)
    language: str = "en"


@router.post("/tts")
@limiter.limit(RATE_LIMITS["api_write"])
async def text_to_speech(
    request: Request,
    body: TTSRequest,
    current_user: User = Depends(get_current_user),
):
    audio = await tts_service.text_to_speech(body.text, voice=body.voice, rate=body.rate)
    if audio is None:
        raise HTTPException(status_code=503, detail="TTS service unavailable")
    return Response(content=audio, media_type="audio/mpeg")


@router.post("/asr")
@limiter.limit(RATE_LIMITS["api_write"])
async def speech_to_text(
    request: Request,
    audio: UploadFile,
    current_user: User = Depends(get_current_user),
    language: str = "zh",
):
    audio_data = await audio.read()
    if not audio_data:
        raise HTTPException(status_code=400, detail="Empty audio file")

    result = await asr_service.transcribe_audio(
        audio_data,
        language=language,
        content_type=audio.content_type,
        filename=audio.filename,
    )
    if result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])

    return {
        "transcript": result["transcript"],
        "language": result["language"],
        "confidence": result["confidence"],
    }


@router.post("/score-pronunciation")
@limiter.limit(RATE_LIMITS["api_write"])
async def score_pronunciation(
    request: Request,
    audio: UploadFile,
    reference_text: str,
    current_user: User = Depends(get_current_user),
    language: str = "en",
):
    audio_data = await audio.read()
    if not audio_data:
        raise HTTPException(status_code=400, detail="Empty audio file")

    result = await asr_service.score_pronunciation(
        audio_data,
        reference_text=reference_text,
        language=language,
        content_type=audio.content_type,
        filename=audio.filename,
    )
    if result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])

    return {
        "score": result["score"],
        "confidence": result["confidence"],
        "transcript": result["transcript"],
    }


@router.get("/voices")
@limiter.limit(RATE_LIMITS["api_read"])
async def list_voices(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return tts_service.get_available_voices()


@router.post("/parse-math")
@limiter.limit(RATE_LIMITS["api_write"])
async def parse_math(
    request: Request,
    body: dict,
    current_user: User = Depends(get_current_user),
):
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="Missing 'text' field")
    return {"parsed": asr_service.parse_math_speech(text)}
