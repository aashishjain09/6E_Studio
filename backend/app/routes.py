from uuid import UUID
from fastapi import APIRouter, HTTPException
import base64
from backend.app.schemas import (
    GenerateRequest,
    GenerateResponse,
    ProjectCreateRequest,
    ProjectResponse,
    AssetUploadRequest,
    AssetResponse,
)
from backend.app.storage import project_store
from backend.app.openai_client import OpenAIClient

router = APIRouter()
openai_client = OpenAIClient()

@router.get("/projects", response_model=list[ProjectResponse])
def list_projects():
    return project_store.list_projects()

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: UUID):
    project = project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects", response_model=ProjectResponse)
def create_project(request: ProjectCreateRequest):
    return project_store.create_project(request)

@router.post("/projects/{project_id}/assets", response_model=AssetResponse)
def upload_asset(project_id: UUID, request: AssetUploadRequest):
    project = project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        content = base64.b64decode(request.content)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 content: {str(e)}")
    
    try:
        asset = project_store.add_asset(project_id, request.filename, request.file_type, content)
        return asset
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload asset: {str(e)}")

@router.get("/projects/{project_id}/assets", response_model=list[AssetResponse])
def list_assets(project_id: UUID):
    project = project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project.assets

@router.delete("/projects/{project_id}/assets/{asset_id}")
def delete_asset(project_id: UUID, asset_id: UUID):
    project = project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    
    success = project_store.delete_asset(project_id, asset_id)
    if not success:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"status": "deleted"}

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
