import pytest

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.db.session import get_db

# Import models so SQLModel knows about them
from app.models.user import User
from app.models.organization import Organization


@pytest.fixture
def client():

    # Temporary database used only for testing
    test_engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False
        },
        poolclass=StaticPool
    )

    # Create the tables inside the temporary database
    SQLModel.metadata.create_all(test_engine)

    # Replace the real PostgreSQL connection
    # with the test database connection
    def override_get_db():

        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Create a fake client that can call our FastAPI routes
    with TestClient(app) as test_client:
        yield test_client

    # Clean everything after the test
    app.dependency_overrides.clear()

    SQLModel.metadata.drop_all(test_engine)