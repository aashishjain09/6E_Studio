# 6E Creative Studio

## Project overview
6E Creative Studio is a hackathon prototype for generating campaign and poster images from user-provided creative briefs. The app includes a backend FastAPI API, a Streamlit frontend, and OpenAI integration scaffolding.

## Architecture
- `backend/` — FastAPI service with project management endpoints, persistence, and OpenAI integration.
- `frontend/` — Streamlit app for landing page, project creation, project list, and explore views.
- `dev.ps1` — PowerShell script to set up the local environment and launch the app in development mode.

## Run the project
1. Open PowerShell in the repo root.
2. Run `./dev.ps1`.
3. Open the frontend at `http://127.0.0.1:8501`.
4. The backend API is available at `http://127.0.0.1:8000`.

## Environment variables
- `OPENAI_API_KEY` — optional, required only if you want the backend to call OpenAI for image/text generation.

## Repo structure
- `tasks.md` — Ashish task list and implementation plan.
- `backend/requirements.txt` — backend Python dependencies.
- `backend/app/main.py` — FastAPI application entrypoint.
- `backend/app/routes.py` — API route definitions.
- `backend/app/schemas.py` — request/response models.
- `backend/app/storage.py` — JSON persistence for projects.
- `backend/app/openai_client.py` — OpenAI request wrapper and fallback.
- `frontend/requirements.txt` — frontend Python dependencies.
- `frontend/app.py` — Streamlit entrypoint.
- `dev.ps1` — script to install dependencies and run backend/frontend in dev mode.
- `.gitignore` — ignore files for Python and local development.

## Notes
- This repository is intentionally minimal and modular so another contributor or coding assistant can continue without making assumptions.
- Project data persists to `backend/data/projects.json` during development.
