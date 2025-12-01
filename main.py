import base64
from pathlib import Path
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import RedirectResponse

from preliminary.library_basics import CodingVideo
from pydantic import BaseModel
import pytesseract
from PIL import Image
import io
from preliminary.llm_runner import run_llm
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="templates/pages")

VIDEOS = {"demo": Path("resources/oop.mp4")}

UPLOAD_DIR = Path("resources")
UPLOAD_DIR.mkdir(exist_ok=True)

def _open_vid_or_404(vid: str) -> CodingVideo:
    path = VIDEOS.get(vid)
    if not path or not path.is_file():
        raise ValueError("Video not found")
    return CodingVideo(path)


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "videos": VIDEOS})

@app.post("/upload")
def upload_video(video: UploadFile = File(...)):
    if not video.filename.lower().endswith(".mp4"):
        return HTMLResponse("<p>Only MP4 allowed</p>")

    save_path = UPLOAD_DIR / video.filename
    with save_path.open("wb") as f:
        shutil.copyfileobj(video.file, f)

    vid_stem = Path(video.filename).stem

    # Add to VIDEOS so dropdown sees it
    VIDEOS[vid_stem] = save_path

    # Redirect directly to OCR page
    return RedirectResponse(f"/video/{vid_stem}/frame_preview/1.0", status_code=303)



@app.get("/video/{vid}/frame_preview/{t}", response_class=HTMLResponse)
def view_frame_preview(request: Request, vid: str, t: int = 1):
    video = _open_vid_or_404(vid)
    try:
        frame_bytes = video.get_image_as_bytes(t)
        frame_b64 = base64.b64encode(frame_bytes).decode()
        return templates.TemplateResponse(
            "ocr.html",
            {
                "request": request,
                "vid": vid,
                "frame_b64": frame_b64,
                "ai_output": "",  # empty initially
            }
        )
    finally:
        video.capture.release()

@app.post("/video/{vid}/extract_ai")
def extract_ai(vid: str, t: float = Form(...)):
    video = _open_vid_or_404(vid)
    try:
        frame_bytes = video.get_image_as_bytes(t)
        frame_b64 = base64.b64encode(frame_bytes).decode()

        image = Image.open(io.BytesIO(frame_bytes))
        ocr_text = pytesseract.image_to_string(image).strip()
        ai_result = run_llm(ocr_text)

        return JSONResponse({
            "ai_output": ai_result,
            "frame_b64": frame_b64
        })
    finally:
        video.capture.release()

