import json
import os
from datetime import datetime
from typing import Any
from uuid import uuid4, UUID

from backend.app.schemas import ProjectCreateRequest, ProjectResponse, AssetResponse

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "projects.json")
ASSETS_DIR = os.path.join(DATA_DIR, "assets")


class ProjectStore:
    def __init__(self, db_file: str = DB_PATH):
        self.db_file = db_file
        self._projects: list[dict] = []
        self._load()

    # ── Persistence ───────────────────────────────────────────────────────────

    def _load(self) -> None:
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(ASSETS_DIR, exist_ok=True)
        if not os.path.exists(self.db_file):
            self._projects = []
            self._save()
            return
        try:
            with open(self.db_file, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
                self._projects = raw if isinstance(raw, list) else []
        except (json.JSONDecodeError, IOError):
            self._projects = []

    def _save(self) -> None:
        with open(self.db_file, "w", encoding="utf-8") as fh:
            json.dump(self._projects, fh, default=str, indent=2)

    # ── Projects ──────────────────────────────────────────────────────────────

    def list_projects(self) -> list[ProjectResponse]:
        return [ProjectResponse(**p) for p in self._projects]

    def get_project(self, project_id: UUID) -> ProjectResponse | None:
        for p in self._projects:
            if p["id"] == str(project_id):
                return ProjectResponse(**p)
        return None

    def create_project(self, request: ProjectCreateRequest) -> ProjectResponse:
        project = ProjectResponse(
            id=uuid4(),
            title=request.title,
            message=request.message,
            channel=request.channel,
            created_at=datetime.utcnow(),
            status="draft",
            assets=[],
        )
        # .model_dump() is the Pydantic v2 API; falls back gracefully if v1 is used.
        self._projects.append(project.model_dump(mode="json"))
        self._save()
        return project

    def update_project(self, project_id: UUID, **updates: Any) -> ProjectResponse:
        for index, p in enumerate(self._projects):
            if p["id"] == str(project_id):
                p.update({k: str(v) if hasattr(v, '__str__') and not isinstance(v, (str, int, float, bool, type(None))) else v
                           for k, v in updates.items() if v is not None})
                self._projects[index] = p
                self._save()
                return ProjectResponse(**p)
        raise ValueError("Project not found")

    # ── Assets ────────────────────────────────────────────────────────────────

    def add_asset(
        self, project_id: UUID, filename: str, file_type: str, content: bytes
    ) -> AssetResponse:
        project, project_index = self._find_project_raw(project_id)

        asset_id = uuid4()
        asset_filename = f"{asset_id}_{filename}"
        asset_dir = os.path.join(ASSETS_DIR, str(project_id))
        os.makedirs(asset_dir, exist_ok=True)

        file_full_path = os.path.join(asset_dir, asset_filename)
        with open(file_full_path, "wb") as fh:
            fh.write(content)

        asset = AssetResponse(
            id=asset_id,
            name=filename,
            file_type=file_type,
            file_path=f"assets/{project_id}/{asset_filename}",
            created_at=datetime.utcnow(),
        )

        project.setdefault("assets", [])
        project["assets"].append(asset.model_dump(mode="json"))
        self._projects[project_index] = project
        self._save()
        return asset

    def delete_asset(self, project_id: UUID, asset_id: UUID) -> bool:
        project, project_index = self._find_project_raw(project_id)

        for idx, asset in enumerate(project.get("assets", [])):
            if asset["id"] == str(asset_id):
                asset_path = os.path.join(DATA_DIR, asset["file_path"])
                if os.path.exists(asset_path):
                    os.remove(asset_path)
                project["assets"].pop(idx)
                self._projects[project_index] = project
                self._save()
                return True
        return False

    # ── Internal ──────────────────────────────────────────────────────────────

    def _find_project_raw(self, project_id: UUID) -> tuple[dict, int]:
        for index, p in enumerate(self._projects):
            if p["id"] == str(project_id):
                return p, index
        raise ValueError("Project not found")


project_store = ProjectStore()