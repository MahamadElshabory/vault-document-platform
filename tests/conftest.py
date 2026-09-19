import pytest

from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, Session, create_engine

from app.main import app
from app.db.session import get_db

from app.models.user import User
from app.models.organization import Organization
from app.models.document import Document


@pytest.fixture
def test_engine():

    engine = create_engine(
        "sqlite://",
        connect_args={
            "check_same_thread": False
        },
        poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)

    yield engine

    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client(test_engine):

    def override_get_db():

        with Session(test_engine) as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def db_session(test_engine):

    with Session(test_engine) as session:
        yield session