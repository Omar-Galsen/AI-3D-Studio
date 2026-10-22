# GPU inference setup (not yet deployed or tested)

## Architecture
Render static site -> Render FastAPI gateway -> self-hosted CUDA GPU worker -> Hunyuan3D-2.1 -> GLB.

**Hunyuan3D 2.1 is image-to-3D**, not direct text-to-3D. For realistic humans, upload a full-body reference image. Text prompts are retained as concept notes only. A separate text-to-image model would be needed to convert text prompts into reference images.

## GPU machine
Use a Linux NVIDIA CUDA GPU machine with at least 10 GB VRAM for shape generation (upstream minimum). A 24 GB+ GPU provides more headroom. Do not attempt on a 2 GB GPU.

Install NVIDIA drivers, Python 3.10, CUDA-compatible PyTorch, and Hunyuan3D-2.1 following its official instructions:
https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1

Install this repo's `gpu-worker/requirements.txt` in the same Python environment.
Set:
- `HUNYUAN_ROOT` to the cloned Hunyuan3D-2.1 folder
- `WORKER_TOKEN` to a long random secret
- `HUNYUAN_MODEL` optionally to a local weights path

Start GPU worker with `uvicorn gpu-worker.app:app --host 0.0.0.0 --port 8080` (from a suitable working directory/import setup; the hyphenated folder name cannot be imported as a Python module; instead run `cd gpu-worker && uvicorn app:app --host 0.0.0.0 --port 8080`).
Place the worker behind HTTPS, authentication, and request limits. A public deployment needs queueing, abuse prevention and persistent storage.

## Render API gateway
Create a separate Render Python Web Service using this same GitHub repository.
- Build: `pip install -r backend/requirements.txt`
- Start: `uvicorn backend.app:app --host 0.0.0.0 --port $PORT`
- Environment: `GPU_WORKER_URL` (HTTPS URL of your worker), `GPU_WORKER_TOKEN` (same secret as WORKER_TOKEN), `FRONTEND_ORIGIN=https://ai-3d-studio-cg4b.onrender.com`
- Do not expose the GPU token in the static website.

Then edit `config.js` to set `window.AI3D_API_URL` to the Render API service HTTPS URL. The browser will call `/api/health` and `/api/generate` there.

## Limits and verification
No worker, model weights or GPU has been provisioned by this commit. Do not describe inference as working until a real image has been converted and GLB opened in the viewer. This synchronous prototype is for one GPU job at a time; add durable job queues before public use.
Review the Tencent Hunyuan3D-2.1 community license, including territorial and commercial terms, before deployment.
