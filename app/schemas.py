# Bu dosya: Pydantic v2 veri şemaları ve doğrulama kuralları
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

class ResizeRequest(BaseModel):
    """Schema representing validation rules for image resizing request parameters."""
    width: int = Field(gt=0, le=4096, description="Target width in pixels (1-4096)")
    height: int = Field(gt=0, le=4096, description="Target height in pixels (1-4096)")
    quality: int = Field(default=85, ge=1, le=100, description="Image quality from 1 to 100")
    format: Literal["JPEG", "PNG", "WEBP"] = Field(default="JPEG", description="Output format of the image")

class ImageResponse(BaseModel):
    """Schema representing metadata and pre-signed download URL of a resized image."""
    id: int
    original_filename: str
    s3_bucket: str
    s3_key: str
    original_width: int
    original_height: int
    resized_width: int
    resized_height: int
    file_size_bytes: int
    content_type: str
    created_at: datetime
    presigned_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class ImageListResponse(BaseModel):
    """Schema representing a paginated list of resized images."""
    items: list[ImageResponse]
    total: int
