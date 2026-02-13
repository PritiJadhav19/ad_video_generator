from pathlib import Path
import edge_tts

async def synthesize(text: str, out_path: Path, voice: str = "hi-IN-MadhurNeural"):
    """
    Async TTS that works inside FastAPI/uvicorn event loop.
    """
    communicate = edge_tts.Communicate(text, voice=voice)
    await communicate.save(str(out_path))