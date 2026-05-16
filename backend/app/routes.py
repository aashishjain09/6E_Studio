from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.app.schemas import (
    GenerateResponse,
    ProjectCreateRequest,
    ProjectResponse,
    SocialMediaRequest, SocialMediaResponse,
    CopywritingRequest, CopywritingResponse,
    BannerDesignRequest, BannerDesignResponse,
    ImagePromptRequest, ImagePromptResponse,
    ImageEditRequest, ImageEditResponse,
    GeminiImageRequest, GeminiImageResponse,
)
from backend.app.storage import project_store
from backend.app.openai_client import OpenAIClient
from backend.app.llm_service import llm_service

router = APIRouter()
openai_client = OpenAIClient()


# ── Project CRUD ──────────────────────────────────────────────────────────────

@router.get("/projects", response_model=list[ProjectResponse])
def list_projects():
    return project_store.list_projects()


@router.post("/projects", response_model=ProjectResponse)
def create_project(request: ProjectCreateRequest):
    return project_store.create_project(request)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str):
    project = project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


class ProjectUpdateRequest(BaseModel):
    title: Optional[str] = None
    message: Optional[str] = None
    channel: Optional[str] = None
    metadata: Optional[dict] = None


@router.patch("/projects/{project_id}", response_model=ProjectResponse)
def update_project_meta(project_id: str, request: ProjectUpdateRequest):
    project = project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    kwargs = {k: v for k, v in request.model_dump().items() if v is not None}
    updated = project_store.update_project(project_id, **kwargs)
    if updated is None:
        raise HTTPException(status_code=500, detail="Update failed")
    return updated


# ── Asset management ──────────────────────────────────────────────────────────

class AssetCreateRequest(BaseModel):
    filename: str
    file_type: str
    content: str  # base64-encoded


@router.post("/projects/{project_id}/assets")
def upload_asset(project_id: str, request: AssetCreateRequest):
    project = project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    asset = project_store.add_asset(
        project_id,
        filename=request.filename,
        file_type=request.file_type,
        content=request.content,
    )
    if asset is None:
        raise HTTPException(status_code=500, detail="Asset upload failed")
    return asset


@router.delete("/projects/{project_id}/assets/{asset_id}")
def delete_asset(project_id: str, asset_id: str):
    project = project_store.get_project(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    ok = project_store.delete_asset(project_id, asset_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Asset not found")
    return {"deleted": asset_id}


# ── Core generation (DALL-E via openai_client) ────────────────────────────────

class GenerateRequestExtended(BaseModel):
    project_id: str
    prompt: Optional[str] = None
    image_prompt: Optional[str] = None  # falls back to prompt if omitted


@router.post("/generate", response_model=GenerateResponse)
def generate_content(request: GenerateRequestExtended):
    project = project_store.get_project(request.project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    text_prompt  = request.prompt or project.message
    image_prompt = request.image_prompt or text_prompt

    generated_text      = openai_client.generate_text(text_prompt)
    generated_image_url = openai_client.generate_image(image_prompt)

    updated_project = project_store.update_project(
        request.project_id,
        generated_text=generated_text,
        generated_image_url=generated_image_url,
        status="generated",
    )

    return GenerateResponse(project=updated_project, status="completed")


# ── Explore ───────────────────────────────────────────────────────────────────

@router.get("/explore", response_model=list[ProjectResponse])
def explore_projects():
    return [
        p for p in project_store.list_projects()
        if p.generated_image_url or p.generated_text
    ]


# ── LLM service routes (Azure OpenAI + Gemini) ───────────────────────────────

@router.post("/generate/social", response_model=SocialMediaResponse)
def generate_social_media(request: SocialMediaRequest):
    result = llm_service.generate_social_content(
        campaign_goal=request.campaign_goal,
        platform=request.platform,
        target_audience=request.target_audience,
        brand_tone=request.brand_tone,
        additional_details=request.additional_details,
    )
    return SocialMediaResponse(**result)


@router.post("/generate/copy", response_model=CopywritingResponse)
def generate_copywriting(request: CopywritingRequest):
    result = llm_service.generate_copy(
        product_service=request.product_service,
        copy_type=request.copy_type,
        tone=request.tone,
        length=request.length,
        key_points=request.key_points,
    )
    return CopywritingResponse(**result)


@router.post("/generate/banner", response_model=BannerDesignResponse)
def generate_banner_design(request: BannerDesignRequest):
    result = llm_service.generate_banner_design(
        dimensions=request.dimensions,
        message=request.message,
        brand_colors=request.brand_colors,
        cta_text=request.cta_text,
    )
    return BannerDesignResponse(**result)


@router.post("/generate/image-prompt", response_model=ImagePromptResponse)
def generate_image_prompt(request: ImagePromptRequest):
    result = llm_service.generate_image_prompt(
        description=request.description,
        style=request.style,
        mood=request.mood,
        context=request.context,
    )
    return ImagePromptResponse(**result)


@router.post("/generate/image-edit", response_model=ImageEditResponse)
def generate_image_edit_instructions(request: ImageEditRequest):
    result = llm_service.generate_image_edit_instructions(
        edit_request=request.edit_request,
        image_context=request.image_context,
        desired_outcome=request.desired_outcome,
    )
    return ImageEditResponse(**result)


@router.post("/generate/gemini-image", response_model=GeminiImageResponse)
def generate_gemini_image(request: GeminiImageRequest):
    result = llm_service.generate_image_with_gemini(
        prompt=request.prompt,
        number_of_images=request.number_of_images,
    )
    return GeminiImageResponse(**result)


# ── Health ────────────────────────────────────────────────────────────────────

@router.get("/health")
def health_check():
    llm_health = llm_service.health_check()
    return {
        "openai_configured": openai_client.api_key is not None,
        **llm_health,
    }