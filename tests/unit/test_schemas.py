# Bu dosya: Pydantic şema doğrulama unit testleri
from datetime import datetime, timezone
import pytest
from pydantic import ValidationError
from app.schemas import ResizeRequest, ImageResponse
from app.models import ImageRecord

@pytest.mark.unit
def test_resize_request_valid():
    """Verifies that a valid set of parameters is accepted by ResizeRequest."""
    req = ResizeRequest(width=300, height=200, quality=90, format="JPEG")
    assert req.width == 300
    assert req.height == 200
    assert req.quality == 90
    assert req.format == "JPEG"

@pytest.mark.unit
def test_resize_request_invalid_width():
    """Verifies that an invalid width (0 or negative) raises a ValidationError."""
    with pytest.raises(ValidationError):
        ResizeRequest(width=0, height=200)
    with pytest.raises(ValidationError):
        ResizeRequest(width=-100, height=200)

@pytest.mark.unit
def test_resize_request_max_dimension():
    """Verifies that a width larger than the limit (4096) raises a ValidationError."""
    with pytest.raises(ValidationError):
        ResizeRequest(width=4097, height=200)

@pytest.mark.unit
def test_resize_request_invalid_format():
    """Verifies that an unsupported format (like GIF) raises a ValidationError."""
    with pytest.raises(ValidationError):
        ResizeRequest(width=300, height=300, format="GIF")

@pytest.mark.unit
def test_image_response_from_orm():
    """Verifies that an ImageRecord ORM model is correctly serialized to ImageResponse using model_validate."""
    record = ImageRecord(
        id=42,
        original_filename="pic.jpg",
        s3_bucket="bucket",
        s3_key="resized/abc_pic.jpg",
        original_width=1000,
        original_height=1000,
        resized_width=200,
        resized_height=200,
        file_size_bytes=4500,
        content_type="image/jpeg",
        created_at=datetime.now(timezone.utc)
    )
    
    resp = ImageResponse.model_validate(record)
    assert resp.id == 42
    assert resp.original_filename == "pic.jpg"
    assert resp.s3_key == "resized/abc_pic.jpg"
    assert resp.original_width == 1000
    assert resp.resized_width == 200
    assert resp.file_size_bytes == 4500
    assert resp.presigned_url is None
