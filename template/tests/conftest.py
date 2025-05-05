import os
import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
import vcr

from app.server import app
from app.models import *
from config.core.database import get_session
from config.core.settings import decode_yaml
from config.core.broker import celery

# Load the environment variables for the test environment
load_dotenv(dotenv_path = ".env.test")

# Set the environment variable for the test environment
@pytest.fixture(scope="session", autouse=True)
def set_test_env_vars():
    os.environ["APP_ENV"] = "test"

# Create the test database engine
db_config = decode_yaml("config/database.yml")["test"]
if db_config["driver"] == "sqlite":
    engine = create_engine(db_config["url"], connect_args={"check_same_thread": False})
else:
    raise ValueError(f"Unsupported test database driver: {db_config['driver']}")

# Create the test database
@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)

# Create a test database session
@pytest.fixture(scope="function")
def db_session():
    with Session(engine) as session:
        yield session

# Create a test client
@pytest.fixture(scope="function")
def client(db_session):
    # Dependency override for FastAPI
    def override_get_session():
        yield db_session
    # Patch the dependency in your app so all routes use the test DB
    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as c:
        yield c

# Create a test Celery instance
@pytest.fixture(scope="function")
def celery_test():
    # configure Celery to use memory backend for testing
    celery.conf.update(
        result_backend='cache+memory://',
        task_always_eager=True
    )
    yield celery
    celery.conf.update(
        result_backend=None,
        task_always_eager=False
    )

# Create a VCR instance.
#
# from tests.vcr_config import my_vcr
#
# @my_vcr.use_cassette('some_api_call.yaml')
# def test_external_api(client):
#     response = client.get("/external-api")
#     assert response.status_code == 200
#
vcr = vcr.VCR(
    cassette_library_dir='tests/cassettes',
    record_mode='once',
    match_on=['uri', 'method'],
)
