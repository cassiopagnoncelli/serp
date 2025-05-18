import pytest
from unittest.mock import patch, AsyncMock, MagicMock

from app.api.auth.token import login_for_access_token
from fastapi.security import OAuth2PasswordRequestForm

@pytest.mark.asyncio
async def test_login_for_access_token_function():
    """
    Test the login_for_access_token function directly, bypassing TestClient 
    which causes asyncpg connection issues.
    """
    # Create mock dependencies
    mock_form_data = MagicMock(spec=OAuth2PasswordRequestForm)
    mock_form_data.username = "test@example.com"
    mock_form_data.password = "securepassword123"
    
    mock_request = MagicMock()
    mock_request.headers = {"user-agent": "test-agent"}
    mock_request.client = MagicMock()
    mock_request.client.host = "127.0.0.1"
    
    # Mock the authentication functions
    mock_user = AsyncMock()
    mock_user.email = "test@example.com"
    
    with patch('app.api.auth.token.find_user_by_email', return_value=mock_user), \
         patch('app.api.auth.token.get_device_info', return_value={"name": "test-device"}), \
         patch('app.api.auth.token.get_location_info', return_value={"city": "Test City"}), \
         patch('app.api.auth.token.login_user_with_password', return_value="test_token_value"):
        
        # Call the function directly
        result = await login_for_access_token(mock_form_data, mock_request)
        
        # Assert the result
        assert result == "test_token_value"
