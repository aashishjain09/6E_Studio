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
        self._projects = []
        self._load()

    def _load(self) -> None:
        if not os.path.isdir(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
        if not os.path.isdir(ASSETS_DIR):
            os.makedirs(ASSETS_DIR, exist_ok=True)
        if not os.path.exists(self.db_file):
            self._projects = []
            self._save()
            return
        try:
            with open(self.db_file, "r", encoding="utf-8") as handle:
                raw = json.load(handle)
                self._projects = raw if isinstance(raw, list) else []
        except (json.JSONDecodeError, IOError):
            self._projects = []

    def _save(self) -> None:
        with open(self.db_file, "w", encoding="utf-8") as handle:
            json.dump(self._projects, handle, default=str, indent=2)

    def list_projects(self) -> list[ProjectResponse]:
        return [ProjectResponse(**project) for project in self._projects]

    def get_project(self, project_id: UUID) -> ProjectResponse | None:
        for project in self._projects:
            if project["id"] == str(project_id):
                return ProjectResponse(**project)
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
        self._projects.append(project.dict())
        self._save()
        return project

    def update_project(self, project_id: UUID, **updates: Any) -> ProjectResponse:
        for index, project in enumerate(self._projects):
            if project["id"] == str(project_id):
                project.update({k: v for k, v in updates.items() if v is not None})
                self._projects[index] = project
                self._save()
                return ProjectResponse(**project)
        raise ValueError("Project not found")

    def add_asset(self, project_id: UUID, filename: str, file_type: str, content: bytes) -> AssetResponse:
        """Add an asset to a project."""
        project = None
        project_index = None
        for index, p in enumerate(self._projects):
            if p["id"] == str(project_id):
                project = p
                project_index = index
                break
        
        if project is None:
            raise ValueError("Project not found")
        
        asset_id = uuid4()
        asset_filename = f"{asset_id}_{filename}"
        asset_path = os.path.join(ASSETS_DIR, str(project_id))
        os.makedirs(asset_path, exist_ok=True)
        
        file_full_path = os.path.join(asset_path, asset_filename)
        with open(file_full_path, "wb") as f:
            f.write(content)
        
        asset = AssetResponse(
            id=asset_id,
            name=filename,
            file_type=file_type,
            file_path=f"assets/{project_id}/{asset_filename}",
            created_at=datetime.utcnow(),
        )
        
        if "assets" not in project:
            project["assets"] = []
        project["assets"].append(asset.dict())
        self._projects[project_index] = project
        self._save()
        return asset

    def delete_asset(self, project_id: UUID, asset_id: UUID) -> bool:
        """Delete an asset from a project."""
        project = None
        project_index = None
        for index, p in enumerate(self._projects):
            if p["id"] == str(project_id):
                project = p
                project_index = index
                break
        
        if project is None:
            raise ValueError("Project not found")
        
        if "assets" not in project:
            return False
        
        for index, asset in enumerate(project["assets"]):
            if asset["id"] == str(asset_id):
                asset_path = os.path.join(DATA_DIR, asset["file_path"])
                if os.path.exists(asset_path):
                    os.remove(asset_path)
                project["assets"].pop(index)
                self._projects[project_index] = project
                self._save()
                return True
        return False

project_store = ProjectStore()
