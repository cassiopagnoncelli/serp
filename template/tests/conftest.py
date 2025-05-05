import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from app.server import app
from app.models import *
from config.core.database import get_session
from lib.core.env import APP_ENV
from config.core.settings import decode_yaml
from config.core.broker import celery

db_config = decode_yaml("config/database.yml")["test"]

# Create the engine at module scope so all fixtures can use it
if db_config["driver"] == "sqlite":
    engine = create_engine(db_config["url"], connect_args={"check_same_thread": False})
else:
    raise ValueError(f"Unsupported test database driver: {db_config['driver']}")

@pytest.fixture(scope="session", autouse=True)
def create_test_db():
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    yield
    SQLModel.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    with Session(engine) as session:
        yield session

@pytest.fixture(scope="function")
def client(db_session):
    # Dependency override for FastAPI
    def override_get_session():
        yield db_session

    # Patch the dependency in your app so all routes use the test DB
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

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
