import base64
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from preliminary.library_basics import CodingVideo

app = FastAPI()
templates = Jinja2Templates(directory="templates/pages")

VIDEOS = {"demo": Path("resources/oop.mp4")}


def _open_vid_or_404(vid: str) -> CodingVideo:
    path = VIDEOS.get(vid)
    if not path or not path.is_file():
        raise ValueError("Video not found")
    return CodingVideo(path)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "videos": VIDEOS})


@app.get("/video/{vid}/frame/{t}", response_class=HTMLResponse)
def view_frame(request: Request, vid: str, t: float = 1.0):
    video = _open_vid_or_404(vid)
    try:
        frame_bytes = video.get_image_as_bytes(t)
        frame_b64 = base64.b64encode(frame_bytes).decode("utf-8")
        ocr_text = "This is a mocked OCR text."
        return templates.TemplateResponse(
            "ocr.html",
            {"request": request, "vid": vid, "frame_b64": frame_b64, "ocr_text": ocr_text}
        )
    finally:
        video.capture.release()
