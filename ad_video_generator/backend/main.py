from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
import uuid

from backend.video_maker import make_ad_video

app = FastAPI(title="Text-to-Ad Video Generator")

# Output folder
OUT_DIR = Path("data/outputs")
OUT_DIR.mkdir(parents=True, exist_ok=True)


class AdRequest(BaseModel):
    brand: str
    product: str
    benefits: list[str]
    audience: str = "India, 18-35"
    offer: str | None = None
    cta: str = "Order Now"
    tone: str = "Relatable, punchy"
    language: str = "Hinglish"   # Hinglish / Hindi / English
    duration_sec: int = 15       # 15 or 30


@app.get("/")
def root():
    return {"status": "ok"}


@app.post("/generate")
async def generate(req: AdRequest):
    job_id = str(uuid.uuid4())[:8]
    out_path = OUT_DIR / f"ad_{job_id}.mp4"

    # ✅ await async video generation
    await make_ad_video(req.model_dump(), out_path)

    return {
        "job_id": job_id,
        "video_path": str(out_path),
        "download_url": f"/download/{job_id}"
    }


@app.get("/download/{job_id}")
def download(job_id: str):
    video_path = OUT_DIR / f"ad_{job_id}.mp4"
    if not video_path.exists():
        return {"error": "Video not found. Generate first."}

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=video_path.name
    )