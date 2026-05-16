from datetime import datetime
from typing import Optional
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
