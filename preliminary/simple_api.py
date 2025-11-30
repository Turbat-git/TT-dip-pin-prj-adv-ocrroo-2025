"""Provides a simple API for your basic OCR client

Drive the API to complete "interprocess communication"

Requirements
"""

from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi import Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from library_basics import CodingVideo
import pytesseract
from PIL import Image
import io
import subprocess
import shlex
import json
from llm_runner import run_llm

app = FastAPI()

templates = Jinja2Templates(directory="templates")


# We'll create a lightweight "database" for our videos
# You can add uploads later (not required for assessment)
# For now, we will just hardcode are samples
VIDEOS: dict[str, Path] = {
    "demo": Path("../resources/oop.mp4")
}


class VideoMetaData(BaseModel):
    fps: float
    frame_count: int
    duration_seconds: float
    _links: dict | None = None


@app.get("/video")
def list_videos():
    """List all available videos with HATEOAS-style links."""
    return {
        "count": len(VIDEOS),
        "videos": [
            {
                "id": vid,
                "path": str(path), # Not standard for debug only
                "_links": {
                    "self": f"/video/{vid}",
                    "frame_example": f"/video/{vid}/frame/1.0"
                }
            }
            for vid, path in VIDEOS.items()
        ]
    }


def _open_vid_or_404(vid: str) -> CodingVideo:
    path = VIDEOS.get(vid)
    if not path or not path.is_file():
        raise HTTPException(status_code=404, detail="Video not found")
    try:
        return CodingVideo(path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Could not open video {e}")


def _meta(video: CodingVideo) -> VideoMetaData:
    return VideoMetaData(
            fps=video.fps,
            frame_count=video.frame_count,
            duration_seconds=video.duration
    )


@app.get("/video/{vid}", response_model=VideoMetaData)
def video(vid: str):
    video = _open_vid_or_404(vid)
    try:
        meta = _meta(video)
        meta._links = {
            "self": f"/video/{vid}",
            "frames": f"/video/{vid}/frame/{{seconds}}"
        }
        return meta
    finally:
        video.capture.release()


@app.get("/video/{vid}/frame/{t}", response_class=Response)
def video_frame(vid: str, t: float):
    try:
        video = _open_vid_or_404(vid)
        return Response(content=video.get_image_as_bytes(t), media_type="image/png")
    finally:
        video.capture.release()


@app.get("/video/{vid}/frame/{t}/ocr")
def video_frame_ocr(request: Request, vid: str, t: float):
    """
    Extracts a frame at `t` seconds from video `vid` and performs OCR on it.
    Returns extracted text as JSON.

    Reference:
    https://pypi.org/project/pytesseract/
    """
    video = _open_vid_or_404(vid)

    try:
        # Get frame image bytes
        frame_bytes = video.get_image_as_bytes(t)

        # Convert to base64 for <img src="...">
        import base64
        frame_b64 = base64.b64encode(frame_bytes).decode()

        # Run OCR
        image = Image.open(io.BytesIO(frame_bytes))
        ocr_text = pytesseract.image_to_string(image).strip()

        extracted_code = run_llm(ocr_text)

        return templates.TemplateResponse(
            "ocr.html",
            {
                "request": request,
                "vid": vid,
                "frame_b64": frame_b64,
                "ocr_text": extracted_code,
            }
        )

    finally:
        video.capture.release()
