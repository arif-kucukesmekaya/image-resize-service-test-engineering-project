# Bu dosya: Test veri fabrikası (factory boy)
from datetime import datetime, timezone
import factory
from factory.alchemy import SQLAlchemyModelFactory
from faker import Faker
from app.models import ImageRecord

fake = Faker()

class ImageRecordFactory(SQLAlchemyModelFactory):
    """Factory for creating mock database records for ImageRecord."""
    class Meta:
        model = ImageRecord
        sqlalchemy_session_persistence = "commit"

    original_filename = factory.LazyFunction(lambda: fake.file_name(extension="jpg"))
    s3_bucket = "image-resize-bucket"
    s3_key = factory.LazyFunction(lambda: f"resized/{fake.uuid4()}.jpg")
    original_width = factory.LazyFunction(lambda: fake.random_int(min=100, max=4000))
    original_height = factory.LazyFunction(lambda: fake.random_int(min=100, max=4000))
    resized_width = factory.LazyFunction(lambda: fake.random_int(min=50, max=800))
    resized_height = factory.LazyFunction(lambda: fake.random_int(min=50, max=800))
    file_size_bytes = factory.LazyFunction(lambda: fake.random_int(min=1000, max=500000))
    content_type = "image/jpeg"
    created_at = factory.LazyFunction(lambda: datetime.now(timezone.utc))
