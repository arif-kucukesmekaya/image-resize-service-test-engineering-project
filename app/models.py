# Bu dosya: Resim metadata veritabanı modeli
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

def utcnow() -> datetime:
    """Returns the current timezone-aware datetime in UTC.

    Returns:
        datetime: Current datetime in UTC timezone.
    """
    return datetime.now(timezone.utc)

class ImageRecord(Base):
    """SQLAlchemy model representing the metadata of a resized image.

    Stored in the 'image_records' table.
    """
    __tablename__ = "image_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    original_filename = Column(String, nullable=False)
    s3_bucket = Column(String, nullable=False)
    s3_key = Column(String, unique=True, nullable=False)
    original_width = Column(Integer, nullable=False)
    original_height = Column(Integer, nullable=False)
    resized_width = Column(Integer, nullable=False)
    resized_height = Column(Integer, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_type = Column(String, nullable=False, default="image/jpeg")
    created_at = Column(DateTime, default=utcnow, nullable=False)
