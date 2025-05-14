import pytest
import asyncio
from fastapi.testclient import TestClient

from app.models.user import User
from app.server import app

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.mark.asyncio
async def test_auth_token_endpoint(test_client):
    user = await User.create(email="test@example.com", password="securepassword123")
    response = test_client.post(
        "/auth/token",
        data={
            "username": "test@example.com",
            "password": "securepassword123"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    assert response.status_code == 200
    token = response.text.strip('"')  # Remove quotes from response
    assert token is not None
