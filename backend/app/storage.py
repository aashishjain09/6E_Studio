import json
import os
from datetime import datetime
from typing import Any
from uuid import uuid4, UUID

from backend.app.schemas import ProjectCreateRequest, ProjectResponse

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DATA_DIR, "projects.json")

class ProjectStore:
    def __init__(self, db_file: str = DB_PATH):
        self.db_file = db_file
        self._projects = []
        self._load()

    def _load(self) -> None:
        if not os.path.isdir(DATA_DIR):
            os.makedirs(DATA_DIR, exist_ok=True)
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

project_store = ProjectStore()
