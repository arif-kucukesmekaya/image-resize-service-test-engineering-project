# Bu dosya: Resim boyutlandırma (Pillow) ve S3 (boto3) servisleri
import io
import os
from typing import Tuple
import boto3
from botocore.exceptions import ClientError
from PIL import Image, UnidentifiedImageError

class ImageResizeService:
    """Service to handle image operations using Pillow."""

    @staticmethod
    def resize(image_bytes: bytes, width: int, height: int, quality: int, fmt: str) -> Tuple[bytes, int, int]:
        """Resizes the given image bytes while maintaining aspect ratio and saving to the target format.

        Args:
            image_bytes: Raw bytes of the image.
            width: Maximum target width.
            height: Maximum target height.
            quality: Compression quality (1-100).
            fmt: Output format (JPEG, PNG, WEBP).

        Returns:
            A tuple of (resized_bytes, final_width, final_height).

        Raises:
            ValueError: If the image bytes are invalid or the format is unsupported.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
        except (UnidentifiedImageError, ValueError, TypeError) as e:
            raise ValueError("Invalid image bytes") from e

        pillow_fmt = fmt.upper()
        if pillow_fmt not in ("JPEG", "PNG", "WEBP"):
            raise ValueError(f"Unsupported format: {fmt}")

        # Convert to RGB if target is JPEG and image has transparency
        if pillow_fmt == "JPEG" and img.mode in ("RGBA", "LA", "P"):
            img = img.convert("RGB")

        # Use thumbnail to scale down maintaining aspect ratio
        img.thumbnail((width, height))

        out_io = io.BytesIO()
        img.save(out_io, format=pillow_fmt, quality=quality)
        resized_bytes = out_io.getvalue()
        return resized_bytes, img.width, img.height

    @staticmethod
    def get_image_dimensions(image_bytes: bytes) -> Tuple[int, int]:
        """Retrieves width and height of an image from raw bytes.

        Args:
            image_bytes: Raw bytes of the image.

        Returns:
            A tuple of (width, height).

        Raises:
            ValueError: If the image bytes are invalid.
        """
        try:
            img = Image.open(io.BytesIO(image_bytes))
            return img.width, img.height
        except (UnidentifiedImageError, ValueError, TypeError) as e:
            raise ValueError("Invalid image bytes") from e


class S3Service:
    """Service to interact with S3 (AWS or LocalStack)."""

    def __init__(self) -> None:
        """Initializes S3Service."""
        pass

    @property
    def client(self):
        """Returns a boto3 S3 client dynamically.

        This allows Moto mock_aws context managers to intercept client creation during tests.
        """
        endpoint_url = os.getenv("AWS_ENDPOINT_URL")
        aws_access_key = os.getenv("AWS_ACCESS_KEY_ID", "test")
        aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", "test")
        region_name = os.getenv("AWS_DEFAULT_REGION", "us-east-1")

        return boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region_name
        )

    def upload(self, bucket: str, key: str, data: bytes, content_type: str) -> None:
        """Uploads object bytes to S3.

        Args:
            bucket: The target S3 bucket.
            key: The S3 key (path).
            data: Raw file bytes to upload.
            content_type: The MIME content type.
        """
        try:
            self.client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=content_type
            )
        except ClientError as e:
            raise RuntimeError(f"Failed to upload object to S3: {e}") from e

    def generate_presigned_url(self, bucket: str, key: str, expiry: int = 3600) -> str:
        """Generates a temporary pre-signed GET URL for download.

        Args:
            bucket: The S3 bucket name.
            key: The S3 key.
            expiry: Expiration duration in seconds.

        Returns:
            A string containing the presigned URL.
        """
        try:
            url = self.client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": key},
                ExpiresIn=expiry
            )
            # Replace localstack container hostname with localhost for host browser compatibility
            if "http://localstack:4566" in url:
                url = url.replace("http://localstack:4566", "http://localhost:4566")
            elif "https://localstack:4566" in url:
                url = url.replace("https://localstack:4566", "https://localhost:4566")
            return url
        except ClientError as e:
            raise RuntimeError(f"Failed to generate presigned URL: {e}") from e

    def delete(self, bucket: str, key: str) -> None:
        """Deletes an object from S3.

        Args:
            bucket: The S3 bucket.
            key: The S3 key.
        """
        try:
            self.client.delete_object(Bucket=bucket, Key=key)
        except ClientError as e:
            raise RuntimeError(f"Failed to delete object from S3: {e}") from e

    def ensure_bucket(self, bucket: str) -> None:
        """Checks if a bucket exists, creating it if it does not.

        Args:
            bucket: The name of the bucket to verify or create.
        """
        try:
            self.client.head_bucket(Bucket=bucket)
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code")
            if error_code in ("404", "NoSuchBucket"):
                region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
                if region == "us-east-1":
                    self.client.create_bucket(Bucket=bucket)
                else:
                    self.client.create_bucket(
                        Bucket=bucket,
                        CreateBucketConfiguration={"LocationConstraint": region}
                    )
            else:
                raise RuntimeError(f"Failed to check/create S3 bucket: {e}") from e
