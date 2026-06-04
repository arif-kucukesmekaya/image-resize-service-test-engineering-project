# Bu dosya: ImageResizeService unit testleri
import io
import pytest
from PIL import Image
from app.services import ImageResizeService

def generate_test_image(width: int, height: int, fmt: str = "JPEG") -> bytes:
    """Helper function to generate an image with specific dimensions and format in memory."""
    img = Image.new("RGB", (width, height), color="blue")
    out = io.BytesIO()
    img.save(out, format=fmt)
    return out.getvalue()

@pytest.mark.unit
def test_resize_returns_correct_dimensions():
    """Verifies that resizing a 200x200 image to max 100x100 results in correct dimensions."""
    orig_bytes = generate_test_image(200, 200)
    resized_bytes, w, h = ImageResizeService.resize(orig_bytes, 100, 100, 85, "JPEG")
    assert w == 100
    assert h == 100

@pytest.mark.unit
def test_resize_jpeg_output():
    """Verifies that resizing with JPEG format produces a valid loadable JPEG image."""
    orig_bytes = generate_test_image(100, 100)
    resized_bytes, w, h = ImageResizeService.resize(orig_bytes, 50, 50, 85, "JPEG")
    
    # Load and verify Pillow can read it
    img = Image.open(io.BytesIO(resized_bytes))
    assert img.format == "JPEG"

@pytest.mark.unit
def test_resize_png_format():
    """Verifies that resizing with PNG format produces a valid loadable PNG image."""
    orig_bytes = generate_test_image(100, 100)
    resized_bytes, w, h = ImageResizeService.resize(orig_bytes, 50, 50, 85, "PNG")
    
    img = Image.open(io.BytesIO(resized_bytes))
    assert img.format == "PNG"

@pytest.mark.unit
def test_resize_webp_format():
    """Verifies that resizing with WEBP format produces a valid loadable WEBP image."""
    orig_bytes = generate_test_image(100, 100)
    resized_bytes, w, h = ImageResizeService.resize(orig_bytes, 50, 50, 85, "WEBP")
    
    img = Image.open(io.BytesIO(resized_bytes))
    assert img.format == "WEBP"

@pytest.mark.unit
def test_get_image_dimensions():
    """Verifies that original dimensions are read correctly from image bytes."""
    orig_bytes = generate_test_image(350, 180)
    w, h = ImageResizeService.get_image_dimensions(orig_bytes)
    assert w == 350
    assert h == 180

@pytest.mark.unit
def test_resize_invalid_bytes():
    """Verifies that passing invalid/corrupt bytes raises a ValueError."""
    with pytest.raises(ValueError, match="Invalid image bytes"):
        ImageResizeService.resize(b"corrupt-data-not-an-image", 100, 100, 85, "JPEG")

@pytest.mark.unit
def test_resize_quality_affects_size():
    """Verifies that compression quality affects file size (quality=10 is smaller than quality=95)."""
    orig_bytes = generate_test_image(800, 800)
    
    low_q_bytes, _, _ = ImageResizeService.resize(orig_bytes, 400, 400, 10, "JPEG")
    high_q_bytes, _, _ = ImageResizeService.resize(orig_bytes, 400, 400, 95, "JPEG")
    
    assert len(low_q_bytes) < len(high_q_bytes)

@pytest.mark.unit
def test_resize_aspect_ratio():
    """Verifies that aspect ratio is preserved in thumbnail mode (e.g. 400x200 resized with max 100x100 should be 100x50)."""
    orig_bytes = generate_test_image(400, 200)
    resized_bytes, w, h = ImageResizeService.resize(orig_bytes, 100, 100, 85, "JPEG")
    
    assert w == 100
    assert h == 50
