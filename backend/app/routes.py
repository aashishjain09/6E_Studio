from uuid import UUID
from fastapi import APIRouter, HTTPException
from backend.app.schemas import (
    GenerateRequest,
    GenerateResponse,
    ProjectCreateRequest,
    ProjectResponse,
)
from backend.app.storage import project_store
from backend.app.openai_client import OpenAIClient

router = APIRouter()
openai_client = OpenAIClient()

@router.get("/projects", response_model=list[ProjectResponse])
def list_projects():
    return project_store.list_projects()

@router.post("/projects", response_model=ProjectResponse)
def create_project(request: ProjectCreateRequest):
    return project_store.create_project(request)

@router.post("/generate", response_model=GenerateResponse)
def generate_content(request: GenerateRequest):
    project = project_store.get_project(request.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    prompt = request.prompt or project.message
    generated_text = openai_client.generate_text(prompt)
    generated_image_url = openai_client.generate_image(prompt)

    updated_project = project_store.update_project(
        request.project_id,
        generated_text=generated_text,
        generated_image_url=generated_image_url,
        status="generated",
    )

    return GenerateResponse(project=updated_project, status="completed")

@router.get("/explore", response_model=list[ProjectResponse])
def explore_projects():
    return [project for project in project_store.list_projects() if project.generated_image_url or project.generated_text]
