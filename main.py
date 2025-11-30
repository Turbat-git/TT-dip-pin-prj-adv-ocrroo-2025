import base64
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from preliminary.library_basics import CodingVideo
from pydantic import BaseModel
import pytesseract
from PIL import Image
import io
from preliminary.llm_runner import run_llm

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
        # Get frame image bytes
        frame_bytes = video.get_image_as_bytes(t)

        # Convert to base64 for <img src="...">
        import base64
        frame_b64 = base64.b64encode(frame_bytes).decode()

        # Run OCR
        image = Image.open(io.BytesIO(frame_bytes))
        ocr_text = pytesseract.image_to_string(image).strip()

        # extracted_code = run_llm(ocr_text)

        return templates.TemplateResponse(
            "ocr.html",
            {
                "request": request,
                "vid": vid,
                "frame_b64": frame_b64,
                # "ocr_text": extracted_code,
                "ocr_text": ocr_text,
            }
        )

    finally:
        video.capture.release()
