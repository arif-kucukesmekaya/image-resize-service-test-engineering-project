# Bu dosya: Pytest ortak fixture tanımları ve test konfigürasyonu
import io
import socket
import threading
import time
import pytest
from fastapi.testclient import TestClient
from moto import mock_aws
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import uvicorn

from app.database import Base, get_db
from app.main import app
from app.services import S3Service

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(name="db_session")
def fixture_db_session():
    """Provides a clean in-memory SQLite database session for each test case."""
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    from tests.factories import ImageRecordFactory
    ImageRecordFactory._meta.sqlalchemy_session = db
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def fixture_client(db_session, mock_s3):
    """Provides a FastAPI TestClient with the database session dependency overridden."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

@pytest.fixture(name="mock_s3")
def fixture_mock_s3():
    """Intercepts boto3 calls using Moto mock_aws and pre-creates the default S3 bucket."""
    with mock_aws():
        import boto3
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="image-resize-bucket")
        yield s3

@pytest.fixture(name="s3_service")
def fixture_s3_service(mock_s3):
    """Provides an S3Service instance backed by mocked AWS S3."""
    return S3Service()

@pytest.fixture(scope="session", name="sample_image_bytes")
def fixture_sample_image_bytes():
    """Generates a standard 100x100 solid red JPEG image in memory for test uploads."""
    img = Image.new("RGB", (100, 100), color="red")
    out = io.BytesIO()
    img.save(out, format="JPEG")
    return out.getvalue()

def get_free_port() -> int:
    """Finds an open ephemeral port on the host machine."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('127.0.0.1', 0))
    port = s.getsockname()[1]
    s.close()
    return port

@pytest.fixture(scope="session", name="live_server")
def fixture_live_server():
    """Spawns the FastAPI application in a background thread for browser/playwright tests.

    Adheres to security principles by listening strictly on localhost. Runs within mock_aws context to mock S3.
    """
    import os
    # Clean up dev.db to ensure a clean slate for E2E tests
    try:
        if os.path.exists("dev.db"):
            os.remove("dev.db")
    except Exception:
        pass

    with mock_aws():
        import boto3
        # Pre-create the bucket in the session S3 mock for uvicorn
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="image-resize-bucket")

        port = get_free_port()
        config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="warning")
        server = uvicorn.Server(config)
        
        thread = threading.Thread(target=server.run)
        thread.daemon = True
        thread.start()
        
        # Wait for uvicorn server startup
        time.sleep(1.0)
        
        yield f"http://127.0.0.1:{port}"
        
        # Graceful shutdown
        server.should_exit = True
        thread.join(timeout=2)
