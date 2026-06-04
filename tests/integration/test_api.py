# Bu dosya: FastAPI endpoint integration testleri
import pytest
from fastapi.testclient import TestClient
from tests.factories import ImageRecordFactory

@pytest.mark.integration
def test_resize_endpoint_success(client: TestClient, mock_s3, sample_image_bytes):
    """POST /resize returns 200 with the resized image metadata."""
    response = client.post(
        "/resize",
        files={"file": ("test.jpg", sample_image_bytes, "image/jpeg")},
        data={"width": 50, "height": 50, "quality": 85, "format": "JPEG"}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "id" in json_data
    assert json_data["original_filename"] == "test.jpg"
    assert json_data["resized_width"] == 50
    assert json_data["resized_height"] == 50
    assert json_data["presigned_url"] is not None

@pytest.mark.integration
def test_resize_endpoint_invalid_file(client: TestClient, mock_s3):
    """POST /resize with invalid file type (like plain text) returns 400."""
    response = client.post(
        "/resize",
        files={"file": ("test.txt", b"plain text data", "text/plain")},
        data={"width": 50, "height": 50, "quality": 85, "format": "JPEG"}
    )
    assert response.status_code == 400
    assert "Uploaded file is not a valid image" in response.json()["detail"]

@pytest.mark.integration
def test_get_images_empty(client: TestClient):
    """GET /images returns total=0 and empty items list when database is empty."""
    response = client.get("/images")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["total"] == 0
    assert json_data["items"] == []

@pytest.mark.integration
def test_get_image_by_id(client: TestClient, db_session, mock_s3):
    """GET /images/{image_id} returns the correct record when it exists."""
    # Create record via Factory
    record = ImageRecordFactory(original_filename="api_fetch.jpg")
    
    response = client.get(f"/images/{record.id}")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["id"] == record.id
    assert json_data["original_filename"] == "api_fetch.jpg"
    assert json_data["presigned_url"] is not None

@pytest.mark.integration
def test_delete_image(client: TestClient, db_session, mock_s3):
    """DELETE /images/{image_id} deletes the DB record and S3 file, returning 204."""
    # Create record
    record = ImageRecordFactory(original_filename="delete_me.jpg", s3_key="resized/delete_me.jpg")
    
    # Pre-upload mock S3 object to prevent errors
    mock_s3.put_object(Bucket="image-resize-bucket", Key="resized/delete_me.jpg", Body=b"image-data")

    # Verify S3 object exists first
    mock_s3.head_object(Bucket="image-resize-bucket", Key="resized/delete_me.jpg")

    # Delete
    response = client.delete(f"/images/{record.id}")
    assert response.status_code == 204

    # Verify deleted from DB
    get_response = client.get(f"/images/{record.id}")
    assert get_response.status_code == 404

    # Verify deleted from S3
    with pytest.raises(Exception):
        mock_s3.head_object(Bucket="image-resize-bucket", Key="resized/delete_me.jpg")

@pytest.mark.integration
def test_health_endpoint(client: TestClient):
    """GET /health returns 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    json_data = response.json()
    assert json_data["status"] == "ok"
    assert "timestamp" in json_data
