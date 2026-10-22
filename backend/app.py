"""AI3D Studio API scaffold. No inference provider is connected."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="AI3D Studio", version="0.1.0")

class GenerationRequest(BaseModel):
    prompt: str = Field(min_length=3, max_length=2000)
    category: str = "human"

@app.get("/api/health")
def health():
    return {"status": "ok", "generation_enabled": False, "provider": None}

@app.post("/api/generate")
def generate(request: GenerationRequest):
    raise HTTPException(status_code=501, detail="No AI 3D inference provider configured. Generation is not available.")
