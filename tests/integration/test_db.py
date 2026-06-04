# Bu dosya: Testcontainers Postgres veritabanı entegrasyon testleri
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from testcontainers.postgres import PostgresContainer

from app.database import Base
from app.models import ImageRecord
from tests.factories import ImageRecordFactory

@pytest.fixture(scope="module", name="pg_engine")
def fixture_pg_engine():
    """Spawns a real PostgreSQL container using testcontainers and returns a SQLAlchemy engine."""
    with PostgresContainer("postgres:15-alpine") as pg:
        connection_url = pg.get_connection_url()
        # Ensure psycopg2 driver is used
        if "postgresql://" in connection_url:
            connection_url = connection_url.replace("postgresql://", "postgresql+psycopg2://")
        engine = create_engine(connection_url)
        Base.metadata.create_all(engine)
        yield engine

@pytest.fixture(name="pg_session")
def fixture_pg_session(pg_engine):
    """Provides a transactional database session for each test, bound to the Postgres container."""
    TestingSession = sessionmaker(bind=pg_engine)
    session = TestingSession()
    # Rebind ImageRecordFactory session to the Postgres session
    ImageRecordFactory._meta.sqlalchemy_session = session
    try:
        yield session
    finally:
        session.rollback()
        # Clean up database tables to ensure isolation between tests
        session.query(ImageRecord).delete()
        session.commit()
        session.close()

@pytest.mark.slow
@pytest.mark.integration
def test_create_image_record(pg_session):
    """Creates an image metadata record using the factory and checks that Postgres auto-assigns an ID."""
    record = ImageRecordFactory(original_filename="postgres_test.jpg")
    
    # Assert ID exists and was committed
    assert record.id is not None
    
    # Query back from DB
    queried = pg_session.query(ImageRecord).filter(ImageRecord.id == record.id).first()
    assert queried is not None
    assert queried.original_filename == "postgres_test.jpg"

@pytest.mark.slow
@pytest.mark.integration
def test_query_image_records(pg_session):
    """Creates 5 image metadata records and verifies that querying all records returns exactly 5."""
    # Seed 5 records
    ImageRecordFactory.create_batch(5)
    
    # Query all
    results = pg_session.query(ImageRecord).all()
    assert len(results) == 5
    
    # Verify IDs are distinct
    ids = {r.id for r in results}
    assert len(ids) == 5
