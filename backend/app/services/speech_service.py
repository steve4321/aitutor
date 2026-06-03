from fastapi import HTTPException, status


async def transcribe_audio(audio_bytes: bytes) -> str:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Speech transcription is not yet available",
    )


async def synthesize_speech(text: str, voice: str = "default") -> bytes:
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Speech synthesis is not yet available",
    )
