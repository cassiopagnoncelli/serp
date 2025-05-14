import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv
from fastapi.testclient import TestClient
import vcr
from tortoise import Tortoise
from tortoise.contrib.test import finalizer, initializer
import asyncio

from app.server import app
from app.models import *
from config.core.settings import decode_yaml
from config.core.broker import celery

# Load the environment variables for the test environment
load_dotenv(dotenv_path = ".env.test")

# Set the environment variable for the test environment
@pytest.fixture(scope="session", autouse=True)
def set_test_env_vars():
    os.environ["APP_ENV"] = "test"

from config.core.tortoise_db import TORTOISE_ORM

@pytest_asyncio.fixture(autouse=True)
async def initialize_tests():
    """Initialize the test database for each test."""
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas()
    yield
    # Clean up all tables
    conn = Tortoise.get_connection("default")
    await conn.execute_query("TRUNCATE TABLE users CASCADE")
    await Tortoise.close_connections()

# Create a test client
@pytest.fixture(scope="function")
def client():
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
