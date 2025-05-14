import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.models.user import User, UserStatus, LoginProvider
from app.utils.authentication import login_user_with_password
from app.server import app

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def mock_user():
    return User(
        id=1,
        uuid="test-uuid",
        account_uuid="account-uuid",
        email="test@example.com",
        name="Test User",
        status=UserStatus.active,
        login_provider=LoginProvider.email,
        enc_password="hashed_password"
    )

@pytest.mark.asyncio
async def test_secure_me_endpoint(test_client, mock_user):
    user = await User.create(
        email="test@example.com",
        password="securepassword123",
        name="Test User",
        account_uuid="account-uuid"
    )
    token = await login_user_with_password(user.email, "securepassword123")
    response = test_client.get(
        "/secure/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"

@pytest.mark.asyncio
async def test_secure_me_endpoint_unauthorized(test_client):
    # Make request without token
    response = test_client.get("/secure/me")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

@pytest.mark.asyncio
async def test_secure_me_endpoint_invalid_token(test_client):
    # Make request with invalid token
    response = test_client.get(
        "/secure/me",
        headers={"Authorization": "Bearer invalid_token"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid authentication credentials"
