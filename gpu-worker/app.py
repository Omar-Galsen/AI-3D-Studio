"""GPU-only Hunyuan3D 2.1 image-to-mesh service.
Requires a separately installed Hunyuan3D-2.1 checkout and CUDA runtime.
Never expose this service publicly without authentication and rate limiting.
"""
import io
import os
import sys
import threading
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError
from starlette.background import BackgroundTask

ROOT = Path(os.environ.get("HUNYUAN_ROOT", "/opt/Hunyuan3D-2.1"))
MODEL = os.environ.get("HUNYUAN_MODEL", "tencent/Hunyuan3D-2.1")
TOKEN = os.environ.get("WORKER_TOKEN")
if not TOKEN:
    raise RuntimeError("WORKER_TOKEN must be set")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "hy3dshape"))
app = FastAPI(title="AI3D GPU Worker")
_lock = threading.Lock()
_pipeline = None

def authorized(authorization: str | None):
    if authorization != f"Bearer {TOKEN}":
        raise HTTPException(401, "Unauthorized")

def load_pipeline():
    global _pipeline
    if _pipeline is None:
        import torch
        if not torch.cuda.is_available():
            raise RuntimeError("CUDA GPU unavailable")
        from hy3dshape.pipelines import Hunyuan3DDiTFlowMatchingPipeline
        _pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(MODEL)
    return _pipeline

@app.get("/health")
def health():
    return {"status": "ready", "model_loaded": _pipeline is not None}

@app.post("/generate")
def generate(image: UploadFile = File(...), authorization: str | None = Header(default=None)):
    authorized(authorization)
    if not _lock.acquire(blocking=False):
        raise HTTPException(429, "GPU busy; try again later")
    try:
        data = image.file.read(8 * 1024 * 1024 + 1)
        if len(data) > 8 * 1024 * 1024:
            raise HTTPException(413, "Image exceeds 8 MB")
        try:
            source = Image.open(io.BytesIO(data))
            source.verify()
            source = Image.open(io.BytesIO(data)).convert("RGBA")
            if source.width * source.height > 16_000_000:
                raise HTTPException(413, "Image resolution too large")
        except (UnidentifiedImageError, OSError, ValueError):
            raise HTTPException(400, "Invalid image")
        directory = TemporaryDirectory()
        try:
            img = Path(directory.name) / "reference.png"
            output = Path(directory.name) / "result.glb"
            source.save(img)
            pipeline = load_pipeline()
            mesh = pipeline(image=str(img))[0]
            mesh.export(str(output))
            if not output.exists() or output.stat().st_size == 0:
                raise RuntimeError("Model did not produce a GLB")
            return FileResponse(output, media_type="model/gltf-binary", filename="generated-character.glb",
                                background=BackgroundTask(directory.cleanup))
        except Exception:
            directory.cleanup()
            raise
    finally:
        _lock.release()
