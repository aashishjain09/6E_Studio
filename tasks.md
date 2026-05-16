# Tasks for Ashish — 6E Creative Studio

## Goal
Build a modular, commit-ready repo for the FastAPI backend and Streamlit frontend so any coding assistant can continue from a clear foundation.

## Progress (completed)
- Repo scaffold created and documented in `README.md`.
- Backend FastAPI entrypoint added: `backend/app/main.py`.
- Backend schemas implemented: `backend/app/schemas.py`.
- JSON-backed storage implemented: `backend/app/storage.py` (writes to `backend/data/projects.json`).
- Backend routes implemented: `backend/app/routes.py` (projects, generate, explore).
- OpenAI wrapper/stub implemented: `backend/app/openai_client.py` (uses `OPENAI_API_KEY` when present, otherwise returns safe fallbacks).
- Streamlit frontend implemented: `frontend/app.py` (Landing, Projects, Explore pages wired to backend).
- Dependency manifests created: `backend/requirements.txt` and `frontend/requirements.txt`.
- Dev tooling added: `dev.ps1` (Windows PowerShell dev launcher) and `.gitignore`.
- Quick validation: Python syntax compiled for created files.

## Next checkpoints (short-term)
1. Commit the current scaffold to git with a descriptive message (done by you to keep commit control).
2. Verify dev environment by running `./dev.ps1` in PowerShell and confirm both services are reachable:
   - Frontend: `http://127.0.0.1:8501`
   - Backend: `http://127.0.0.1:8000`
3. Add basic API integration tests for `GET /api/projects` and `POST /api/projects`.
4. Swap JSON persistence for a simple SQLite DB (proposed migration plan below).

## Next checkpoints (mid-term)
- Implement robust OpenAI integration and safe-rate limiting; add config for `OPENAI_API_KEY` usage.
- Add project detail view in the frontend to inspect and re-run generation with overrides.
- Add storage cleanup and image caching for generated images.

## Next checkpoints (long-term)
- Add CI (GitHub Actions) to run linting and tests on PRs.
- Add unit and integration tests for generation flow using recorded fixtures/mocks.
- Improve frontend UX and design handoff for Simran to implement visuals.

## Notes / Handoff
- Current scaffold intentionally keeps the OpenAI calls stubbed when `OPENAI_API_KEY` is not set so the repo is safe to run without secrets.
- Project data is saved to `backend/data/projects.json`; back this up before migrating to a DB.
- I have not committed these changes to git; please commit when ready so we can continue with feature branches.

## How to commit (suggested)
Open PowerShell in the repo root and run:

```powershell
git add .
git commit -m "chore: scaffold FastAPI + Streamlit app, add dev script and initial implementation"
git branch -M main
git push -u origin main
```

After you commit, tell me and I will continue with the next checkpoint you choose.
