import io
import base64
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from preliminary.library_basics import CodingVideo
from PIL import Image
import easyocr  # <- new OCR library

app = FastAPI()
templates = Jinja2Templates(directory="templates/pages")

VIDEOS = {"demo": Path("resources/oop.mp4")}

# Initialize EasyOCR reader once (CPU-only here)
reader = easyocr.Reader(['en'], gpu=False)


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
        frame_b64 = base64.b64encode(frame_bytes).decode()

        # Run OCR using EasyOCR
        image = Image.open(io.BytesIO(frame_bytes))
        # EasyOCR expects file path or numpy array
        import numpy as np
        img_array = np.array(image)
        result = reader.readtext(img_array)
        ocr_text = " ".join([res[1] for res in result])  # Combine detected text

        return templates.TemplateResponse(
            "ocr.html",
            {
                "request": request,
                "vid": vid,
                "frame_b64": frame_b64,
                "ocr_text": ocr_text,
            }
        )

    finally:
        video.capture.release()
