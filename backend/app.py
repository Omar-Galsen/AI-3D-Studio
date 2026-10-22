"""Public API gateway; deploy separately from the static Render website."""
import os
import httpx
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

app = FastAPI(title="AI3D Studio API", version="0.2.0")
origin = os.environ.get("FRONTEND_ORIGIN", "https://ai-3d-studio-cg4b.onrender.com")
app.add_middleware(CORSMiddleware, allow_origins=[origin], allow_methods=["GET","POST"], allow_headers=["Content-Type"])
worker_url = os.environ.get("GPU_WORKER_URL", "").rstrip("/")
worker_token = os.environ.get("GPU_WORKER_TOKEN", "")

@app.get("/api/health")
async def health():
    return {"status": "ok", "generation_enabled": bool(worker_url and worker_token), "mode": "image-to-3d"}

@app.post("/api/generate")
async def generate(image: UploadFile = File(...)):
    if not worker_url or not worker_token:
        raise HTTPException(503, "GPU worker is not configured")
    data = await image.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise HTTPException(413, "Image exceeds 8 MB")
    if image.content_type not in ("image/png","image/jpeg","image/webp"):
        raise HTTPException(415, "Upload a PNG, JPEG, or WebP reference")
    try:
        async with httpx.AsyncClient(timeout=600) as client:
            result = await client.post(worker_url + "/generate",
                headers={"Authorization": "Bearer " + worker_token},
                files={"image": ("reference.png", data, image.content_type)})
        if result.status_code != 200:
            raise HTTPException(502, "GPU worker failed: " + result.text[:300])
        if not result.content.startswith(b"glTF"):
            raise HTTPException(502, "GPU worker returned an invalid GLB")
        return Response(result.content, media_type="model/gltf-binary",
                        headers={"Content-Disposition": 'attachment; filename="generated-character.glb"'})
    except httpx.RequestError:
        raise HTTPException(502, "GPU worker unavailable")
