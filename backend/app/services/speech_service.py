async def transcribe_audio(audio_bytes: bytes) -> str:
    raise NotImplementedError


async def synthesize_speech(text: str, voice: str = "default") -> bytes:
    raise NotImplementedError
