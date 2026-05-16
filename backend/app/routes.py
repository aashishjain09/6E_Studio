from uuid import UUID
from fastapi import APIRouter, HTTPException
from backend.app.schemas import (
    GenerateRequest,
    GenerateResponse,
    ProjectCreateRequest,
    ProjectResponse,
    SocialMediaRequest,
    SocialMediaResponse,
    CopywritingRequest,
    CopywritingResponse,
    BannerDesignRequest,
    BannerDesignResponse,
    ImagePromptRequest,
    ImagePromptResponse,
    ImageEditRequest,
    ImageEditResponse,
    GeminiImageRequest,
    GeminiImageResponse,
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



@router.post("/generate/social", response_model=SocialMediaResponse)
def generate_social_media(request: SocialMediaRequest):
    """
    Generate social media content (caption, hashtags, image prompt, CTA)
    
    Example request:
    {
        "campaign_goal": "Launch new eco-friendly water bottle",
        "platform": "Instagram",
        "target_audience": "Environmentally conscious millennials",
        "brand_tone": "inspirational",
        "additional_details": "Focus on sustainability and style"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "caption": "🌍 Stay hydrated, save the planet! ✨...",
            "hashtags": ["#EcoFriendly", "#Sustainability"],
            "image_prompt": "Modern reusable water bottle...",
            "cta": "Shop Now",
            "best_time": "9 AM - 11 AM"
        }
    }
    """
    result = llm_service.generate_social_content(
        campaign_goal=request.campaign_goal,
        platform=request.platform,
        target_audience=request.target_audience,
        brand_tone=request.brand_tone,
        additional_details=request.additional_details
    )
    return SocialMediaResponse(**result)


@router.post("/generate/copy", response_model=CopywritingResponse)
def generate_copywriting(request: CopywritingRequest):
    """
    Generate marketing copy (headline, body copy, CTA)
    
    Example request:
    {
        "product_service": "AI-powered email marketing tool",
        "copy_type": "landing page",
        "tone": "professional",
        "length": "medium",
        "key_points": "Easy to use, increases open rates by 40%"
    }
    """
    result = llm_service.generate_copy(
        product_service=request.product_service,
        copy_type=request.copy_type,
        tone=request.tone,
        length=request.length,
        key_points=request.key_points
    )
    return CopywritingResponse(**result)


@router.post("/generate/banner", response_model=BannerDesignResponse)
def generate_banner_design(request: BannerDesignRequest):
    """
    Generate banner design specifications
    
    Example request:
    {
        "dimensions": "1200x628",
        "message": "Summer Sale - Up to 50% Off",
        "brand_colors": "Blue (#1E90FF) and Orange (#FF6347)",
        "cta_text": "Shop Now"
    }
    """
    result = llm_service.generate_banner_design(
        dimensions=request.dimensions,
        message=request.message,
        brand_colors=request.brand_colors,
        cta_text=request.cta_text
    )
    return BannerDesignResponse(**result)


@router.post("/generate/image-prompt", response_model=ImagePromptResponse)
def generate_image_prompt(request: ImagePromptRequest):
    """
    Optimize image generation prompt for DALL-E or similar models
    
    Example request:
    {
        "description": "A modern office workspace with plants",
        "style": "photorealistic",
        "mood": "calm and productive",
        "context": "website hero image"
    }
    """
    result = llm_service.generate_image_prompt(
        description=request.description,
        style=request.style,
        mood=request.mood,
        context=request.context
    )
    return ImagePromptResponse(**result)


@router.post("/generate/image-edit", response_model=ImageEditResponse)
def generate_image_edit_instructions(request: ImageEditRequest):
    """
    Generate image editing instructions
    
    Example request:
    {
        "edit_request": "Remove background and make it white",
        "image_context": "Product photo of a blue water bottle",
        "desired_outcome": "Clean product shot on pure white background"
    }
    """
    result = llm_service.generate_image_edit_instructions(
        edit_request=request.edit_request,
        image_context=request.image_context,
        desired_outcome=request.desired_outcome
    )
    return ImageEditResponse(**result)


@router.post("/generate/gemini-image", response_model=GeminiImageResponse)
def generate_gemini_image(request: GeminiImageRequest):
    """
    Generate image using Google Gemini (Imagen 4.0)
    
    Example request:
    {
        "prompt": "A serene mountain landscape at sunset with vibrant colors",
        "number_of_images": 1
    }
    
    Note: Images are returned as base64-encoded data or URLs
    """
    result = llm_service.generate_image_with_gemini(
        prompt=request.prompt,
        number_of_images=request.number_of_images
    )
    return GeminiImageResponse(**result)


# ============================================================
# HEALTH CHECK FOR LLM SERVICE
# ============================================================
@router.get("/llm/health")
def llm_health_check():
    """
    Check if LLM services are properly configured
    
    Returns status of Azure OpenAI and Gemini integration
    """
    health = llm_service.health_check()
    return health
