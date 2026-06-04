# Bu dosya: S3Service integration testleri
import pytest
from app.services import S3Service

@pytest.mark.integration
def test_upload_and_retrieve(s3_service: S3Service, mock_s3):
    """Verifies that uploading an object puts it in the mocked S3 bucket."""
    bucket = "image-resize-bucket"
    key = "test_upload.jpg"
    data = b"fake-resized-image-bytes"

    s3_service.upload(bucket, key, data, "image/jpeg")

    # Verify using boto3 client mock directly
    response = mock_s3.get_object(Bucket=bucket, Key=key)
    assert response["Body"].read() == data
    assert response["ContentType"] == "image/jpeg"

@pytest.mark.integration
def test_presigned_url_generated(s3_service: S3Service):
    """Verifies that generating a pre-signed URL returns a non-empty HTTP string."""
    bucket = "image-resize-bucket"
    key = "test_url.jpg"

    url = s3_service.generate_presigned_url(bucket, key)
    assert isinstance(url, str)
    assert url.startswith("http")
    assert key in url

@pytest.mark.integration
def test_delete_removes_object(s3_service: S3Service, mock_s3):
    """Verifies that deleting an S3 object removes it from the bucket."""
    bucket = "image-resize-bucket"
    key = "test_delete.jpg"
    data = b"delete-bytes"

    # Pre-upload
    s3_service.upload(bucket, key, data, "image/jpeg")
    
    # Delete
    s3_service.delete(bucket, key)

    # Assert object is gone
    with pytest.raises(mock_s3.exceptions.ClientError):
        mock_s3.get_object(Bucket=bucket, Key=key)

@pytest.mark.integration
def test_ensure_bucket_idempotent(s3_service: S3Service, mock_s3):
    """Verifies that calling ensure_bucket on an existing or new bucket is idempotent and error-free."""
    bucket_name = "brand-new-bucket"

    # Call 1 (creates bucket)
    s3_service.ensure_bucket(bucket_name)
    # Check it exists
    mock_s3.head_bucket(Bucket=bucket_name)

    # Call 2 (idempotent check - shouldn't raise exception)
    s3_service.ensure_bucket(bucket_name)
