# AI 3D Studio

Browser-based 3D character concept studio. The initial version has a procedural human mannequin, editable prompt, orbit controls and GLB export. **It does not generate AI meshes yet.**

## Run
Open `index.html` using a local web server or GitHub Pages. Three.js loads from a public CDN, so an internet connection is required.

## Backend (optional)
```
pip install -r backend/requirements.txt
uvicorn backend.app:app --reload
```
`GET /api/health` reports the backend status. `POST /api/generate` intentionally returns HTTP 501 until a real inference provider is configured.

## Roadmap
- Connect a licensed text/image-to-3D model provider and implement asynchronous jobs.
- Validate generated meshes and support GLB downloads.
- Improve realistic human anatomy, clothing, rigging and textures.

No API keys should be placed in browser JavaScript or committed to GitHub.
