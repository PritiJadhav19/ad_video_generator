from __future__ import annotations

import uuid
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

# ✅ IMPORTANT:
# If your repo is structured like:
# ad_video_generator/
#   backend/
#     main.py
#     video_maker.py
# then use absolute import like below:
from ad_video_generator.backend.video_maker import make_ad_video

app = FastAPI(title="Text-to-Ad Video Generator")

# ✅ Output folder relative to project (stable on Streamlit/GitHub/Windows)
BASE_DIR = Path(__file__).resolve().parents[1]  # .../ad_video_generator
OUT_DIR = BASE_DIR / "data" / "outputs"
OUT_DIR.mkdir(parents=True, exist_ok=True)


class AdRequest(BaseModel):
    brand: str = Field(default="Brand")
    product: str = Field(default="Product")
    benefits: List[str] = Field(default_factory=list)

    audience: str = Field(default="India, 18-35")
    offer: Optional[str] = None
    cta: str = Field(default="Order Now")

    tone: str = Field(default="Relatable, punchy")
    language: str = Field(default="Hinglish")   # Hinglish / Hindi / English
    duration_sec: int = Field(default=15, ge=5, le=60)  # safe range


@app.get("/")
def root():
    return {"status": "ok", "service": "Text-to-Ad Video Generator"}


@app.post("/generate")
async def generate(req: AdRequest):
    job_id = uuid.uuid4().hex[:8]
    out_path = OUT_DIR / f"ad_{job_id}.mp4"

    try:
        await make_ad_video(req.model_dump(), out_path)
    except Exception as e:
        # show a clean error in API response
        raise HTTPException(status_code=500, detail=f"Video generation failed: {e}")

    return {
        "job_id": job_id,
        "video_path": str(out_path),
        "download_url": f"/download/{job_id}",
    }


@app.get("/download/{job_id}")
def download(job_id: str):
    video_path = OUT_DIR / f"ad_{job_id}.mp4"
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found. Generate first.")

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=video_path.name,
    )
