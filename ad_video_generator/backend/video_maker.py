from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any, Optional

import numpy as np
from PIL import Image, ImageDraw, ImageFont

from moviepy.editor import ImageClip, AudioFileClip, concatenate_videoclips

# ✅ IMPORTANT: absolute imports (fixes "No module named backend" on cloud)
from ad_video_generator.backend.script_engine import generate_ad_json
from ad_video_generator.backend.voice import synthesize

W, H = 1080, 1920


# -----------------------------
# Helpers: background + fonts
# -----------------------------
def make_gradient_bg() -> Image.Image:
    top = np.array([20, 20, 60], dtype=np.float32)
    bottom = np.array([70, 40, 150], dtype=np.float32)

    img = np.zeros((H, W, 3), dtype=np.uint8)
    for y in range(H):
        t = y / (H - 1)
        color = top * (1 - t) + bottom * t
        img[y, :, :] = color.astype(np.uint8)
    return Image.fromarray(img)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    # Windows fonts (local dev)
    candidates = [
        r"C:\Windows\Fonts\arialbd.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\calibri.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ]
    for fp in candidates:
        if Path(fp).exists():
            try:
                return ImageFont.truetype(fp, size=size)
            except Exception:
                pass
    return ImageFont.load_default()


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int) -> List[str]:
    words = text.split()
    lines: List[str] = []
    cur: List[str] = []

    for w in words:
        test = " ".join(cur + [w])
        bbox = draw.textbbox((0, 0), test, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width:
            cur.append(w)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [w]

    if cur:
        lines.append(" ".join(cur))
    return lines


def draw_centered_text_block(
    img: Image.Image,
    lines: List[str],
    y_center: int,
    font: ImageFont.ImageFont,
    fill=(255, 255, 255),
    shadow=True,
    line_gap=18,
) -> None:
    draw = ImageDraw.Draw(img)

    sizes = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        sizes.append((w, h))

    total_h = sum(h for _, h in sizes) + line_gap * (len(lines) - 1)
    y = y_center - total_h // 2

    for (line, (w, h)) in zip(lines, sizes):
        x = (W - w) // 2
        if shadow:
            draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0))
        draw.text((x, y), line, font=font, fill=fill)
        y += h + line_gap


def build_frame(
    on_screen_lines: List[str],
    footer: str = "Swipe up / Learn more",
    badge: Optional[str] = None,
) -> np.ndarray:
    bg = make_gradient_bg()
    draw = ImageDraw.Draw(bg)

    main_text = " ".join([t.strip() for t in on_screen_lines if t and t.strip()]) or " "
    font_main = load_font(74)
    max_width = W - 140

    wrapped = wrap_text(draw, main_text, font_main, max_width=max_width)[:4]
    draw_centered_text_block(bg, wrapped, y_center=H // 2, font=font_main)

    # CTA footer
    font_footer = load_font(44)
    footer_lines = wrap_text(draw, footer, font_footer, max_width=max_width)[:2]
    footer_y = H - 220
    for i, line in enumerate(footer_lines):
        bbox = draw.textbbox((0, 0), line, font=font_footer)
        fw = bbox[2] - bbox[0]
        x = (W - fw) // 2
        y = footer_y + i * 54
        draw.text((x + 2, y + 2), line, font=font_footer, fill=(0, 0, 0))
        draw.text((x, y), line, font=font_footer, fill=(255, 255, 255))

    # Badge
    if badge:
        font_badge = load_font(48)
        text = badge.strip()
        pad_x, pad_y = 30, 18
        bbox = draw.textbbox((0, 0), text, font=font_badge)
        bw = (bbox[2] - bbox[0]) + pad_x * 2
        bh = (bbox[3] - bbox[1]) + pad_y * 2

        x0, y0 = 60, 90
        draw.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=24, fill=(255, 255, 255))
        draw.text((x0 + pad_x, y0 + pad_y), text, font=font_badge, fill=(0, 0, 0))

    return np.array(bg)


# -----------------------------
# Pillow-safe zoom helper
# -----------------------------
def _lanczos():
    # Pillow compatibility: Resampling.LANCZOS (new) vs Image.LANCZOS (old)
    if hasattr(Image, "Resampling"):
        return Image.Resampling.LANCZOS
    return Image.LANCZOS


def zoom_frame(frame: np.ndarray, scale: float) -> np.ndarray:
    """
    Zoom frame safely with Pillow and center-crop back to W x H.
    """
    if scale <= 1.0:
        return frame

    img = Image.fromarray(frame)
    new_w = max(int(W * scale), W)
    new_h = max(int(H * scale), H)

    img2 = img.resize((new_w, new_h), resample=_lanczos())

    left = (new_w - W) // 2
    top = (new_h - H) // 2
    img2 = img2.crop((left, top, left + W, top + H))
    return np.array(img2)


# -----------------------------
# Motion + text timing
# -----------------------------
def apply_scene_motion(clip: ImageClip, mode: str, dur: float) -> ImageClip:
    mode = (mode or "").lower()
    dur = max(float(dur), 0.001)

    def transform(frame: np.ndarray, t: float) -> np.ndarray:
        # default gentle zoom
        z = 1.0 + 0.04 * (t / dur)

        if "zoom" in mode:
            z = 1.0 + 0.06 * (t / dur)
        elif "shake" in mode:
            z = 1.0 + 0.03 * (t / dur)

        out = zoom_frame(frame, z)

        if "shake" in mode and t < 0.6:
            dx = int(4 * np.sin(45 * t))
            dy = int(4 * np.cos(38 * t))
            out = np.roll(out, shift=(dy, dx), axis=(0, 1))

        return out

    # ✅ MoviePy-safe: per-frame effect
    return clip.fl_image(lambda frame: transform(frame, clip.t))


def apply_text_animation_timing(clip: ImageClip, anim: str) -> ImageClip:
    anim = (anim or "").lower()

    if anim in ("pop_in", "cta_bounce"):
        def transform(frame: np.ndarray, t: float) -> np.ndarray:
            s = 0.92 + 0.08 * min(t / 0.25, 1.0)
            return zoom_frame(frame, s)

        return clip.fl_image(lambda frame: transform(frame, clip.t))

    if anim in ("slide_up",):
        return clip.set_position(lambda t: (0, int(40 * (1 - min(t / 0.35, 1.0)))))

    if anim in ("swipe_cut", "split_wipe"):
        return clip.set_position(lambda t: (int(6 * np.sin(35 * t)) if t < 0.25 else 0, 0))

    if anim in ("type_on", "glitch"):
        return clip.set_position(lambda t: (int(3 * np.sin(50 * t)) if t < 0.6 else 0, 0))

    return clip


# -----------------------------
# Scene builder (async TTS)
# -----------------------------
async def make_scene(scene: Dict[str, Any], idx: int, tmp_dir: Path) -> ImageClip:
    dur = float(scene.get("t_end", 0) - scene.get("t_start", 0))
    if dur <= 0:
        dur = 1.0

    badge: Optional[str] = None
    on_screen = scene.get("on_screen_text", []) or []

    if scene.get("overlay"):
        for item in scene["overlay"]:
            if isinstance(item, str) and item.upper() in ("SALE", "NEW", "LIMITED TIME", "LIMITED"):
                badge = item.upper()
                break

    anim = scene.get("text_animation") or scene.get("animation") or "pop_in"
    motion = scene.get("camera") or "zoom"

    frame = build_frame(on_screen, footer="Swipe up / Learn more", badge=badge)
    img_path = tmp_dir / f"frame_{idx:02d}.png"
    Image.fromarray(frame).save(img_path)

    vo_text = (scene.get("vo") or "").strip() or " "
    vo_path = tmp_dir / f"vo_{idx:02d}.mp3"
    await synthesize(vo_text, vo_path)

    audio = AudioFileClip(str(vo_path))

    # Duration matching
    if audio.duration and audio.duration > dur:
        audio = audio.subclip(0, dur)
        clip = ImageClip(str(img_path)).set_duration(dur)
    else:
        safe_dur = float(audio.duration) if audio.duration else dur
        clip = ImageClip(str(img_path)).set_duration(safe_dur)

    clip = apply_scene_motion(clip, motion, clip.duration)
    clip = apply_text_animation_timing(clip, anim)

    return clip.set_audio(audio)


# -----------------------------
# Main entry: make_ad_video
# -----------------------------
async def make_ad_video(meta: Dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = out_path.parent / "tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    ad = generate_ad_json(meta)
    scenes = ad.get("scenes", [])
    if not scenes:
        raise ValueError("No scenes generated. Check script_engine.py")

    clips: List[ImageClip] = []
    for i, scene in enumerate(scenes):
        clips.append(await make_scene(scene, i, tmp_dir))

    final = concatenate_videoclips(clips, method="compose")

    final.write_videofile(
        str(out_path),
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=2,
    )
