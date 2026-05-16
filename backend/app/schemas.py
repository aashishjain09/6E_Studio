from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, HttpUrl

class ProjectCreateRequest(BaseModel):
    title: str = Field(..., description="Project title")
    message: str = Field(..., description="Creative brief or campaign description")
    channel: Optional[str] = Field(None, description="Optional destination or audience channel")

class ProjectResponse(BaseModel):
    id: UUID
    title: str
    message: str
    channel: Optional[str] = None
    created_at: datetime
    generated_text: Optional[str] = None
    generated_image_url: Optional[HttpUrl] = None
    status: str = "draft"

class GenerateRequest(BaseModel):
    project_id: UUID
    prompt: Optional[str] = Field(None, description="Optional prompt override for generation")

class GenerateResponse(BaseModel):
    project: ProjectResponse
    status: str


# Social Media Schemas
class SocialMediaRequest(BaseModel):
    campaign_goal: str = Field(..., description="Campaign objective (e.g., 'Increase product awareness')")
    platform: str = Field(default="Instagram", description="Social platform (Instagram, Facebook, LinkedIn, Twitter)")
    target_audience: str = Field(default="General audience", description="Target audience description")
    brand_tone: str = Field(default="professional", description="Brand voice (professional, casual, playful, inspirational)")
    additional_details: Optional[str] = Field(default="", description="Any additional context")

class SocialMediaResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Copywriting Schemas
class CopywritingRequest(BaseModel):
    product_service: str = Field(..., description="Product or service to write about")
    copy_type: str = Field(default="description", description="Type: description, ad copy, email, landing page, tagline")
    tone: str = Field(default="professional", description="Tone: professional, conversational, authoritative, friendly, urgent")
    length: str = Field(default="medium", description="Length: short, medium, long")
    key_points: Optional[str] = Field(default="", description="Key selling points")

class CopywritingResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Banner Design Schemas
class BannerDesignRequest(BaseModel):
    dimensions: str = Field(default="1200x628", description="Banner dimensions (e.g., 1200x628, 728x90)")
    message: str = Field(..., description="Main message for the banner")
    brand_colors: str = Field(default="use vibrant colors", description="Color scheme or brand colors")
    cta_text: str = Field(default="Learn More", description="Call-to-action button text")

class BannerDesignResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Image Generation Schemas
class ImagePromptRequest(BaseModel):
    description: str = Field(..., description="Basic description of desired image")
    style: str = Field(default="realistic", description="Style: realistic, digital art, illustration, 3D render")
    mood: str = Field(default="professional", description="Mood: professional, energetic, calm, dramatic")
    context: str = Field(default="social media", description="Usage context: social media, website, print, ad")

class ImagePromptResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Image Edit Schemas
class ImageEditRequest(BaseModel):
    edit_request: str = Field(..., description="What needs to be edited")
    image_context: str = Field(default="", description="Description of current image")
    desired_outcome: str = Field(default="", description="What final result should look like")

class ImageEditResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Gemini Image Generation Schemas
class GeminiImageRequest(BaseModel):
    prompt: str = Field(..., description="Image generation prompt for Gemini (Imagen 4.0)")
    number_of_images: int = Field(default=1, ge=1, le=4, description="Number of images to generate (1-4)")

class GeminiImageResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
