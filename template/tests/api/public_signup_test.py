import pytest
import httpx
from httpx import ASGITransport
from app.server import app

@pytest.fixture
def client():
    return httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

@pytest.mark.asyncio
async def test_successful_signup(client):
    # Make the signup request
    response = await client.post(
        "/public/signup",
        params={
            "email": "test@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
            "name": "Test User"
        }
    )
    
    # Check API response
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "password" not in data  # Ensure password is not returned

@pytest.mark.asyncio
async def test_duplicate_user_signup(client):
    # First signup
    await client.post(
        "/public/signup",
        params={
            "email": "test@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        }
    )
    
    # Attempt to signup with same email
    response = await client.post(
        "/public/signup",
        params={
            "email": "test@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User already exists"

@pytest.mark.asyncio
async def test_password_mismatch(client):
    response = await client.post(
        "/public/signup",
        params={
            "email": "test@example.com",
            "password": "securepassword123",
            "confirm_password": "differentpassword"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Passwords do not match"

@pytest.mark.asyncio
async def test_invalid_email_format(client):
    response = await client.post(
        "/public/signup",
        params={
            "email": "invalid-email",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        }
    )
    assert response.status_code == 422  # Validation error

@pytest.mark.asyncio
async def test_signup_with_optional_fields(client):
    response = await client.post(
        "/public/signup",
        params={
            "email": "test@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
            "name": "Test User",
            "account_uuid": "123e4567-e89b-12d3-a456-426614174000"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] == "Test User"
    assert "password" not in data

@pytest.mark.asyncio
async def test_signup_without_optional_fields(client):
    response = await client.post(
        "/public/signup",
        params={
            "email": "test@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["name"] is None
    assert "password" not in data
