import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException

from app.utils.authentication import (
    find_user_by_email,
    authenticate_user,
    generate_user_token,
    decode_user_token,
    random_password,
    persist_user_token,
    get_current_user,
    login_user_with_password,
    SECRET_KEY,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.user import User, UserStatus, LoginProvider
from app.schemas.user import UserTokenizable
from app.schemas.token import TokenSchema, CreateTokenSchema


@pytest.mark.asyncio
async def test_find_user_by_email_found():
    """Test that finding a user by email works when user exists"""
    email = "test@example.com"
    mock_user = AsyncMock()
    mock_user.email = email
    
    # Mock User.filter to return a query that returns our mock user
    with patch("app.utils.authentication.User.filter") as mock_filter:
        mock_query = AsyncMock()
        mock_query.first.return_value = mock_user
        mock_filter.return_value = mock_query
        
        result = await find_user_by_email(email)
        
        # Assert result is correct
        assert result == mock_user
        # Assert filter was called with correct email
        mock_filter.assert_called_once_with(email=email)


@pytest.mark.asyncio
async def test_find_user_by_email_not_found():
    """Test that finding a user by email returns None when user doesn't exist"""
    email = "nonexistent@example.com"
    
    # Mock User.filter to return a query that returns None
    with patch("app.utils.authentication.User.filter") as mock_filter:
        mock_query = AsyncMock()
        mock_query.first.return_value = None
        mock_filter.return_value = mock_query
        
        result = await find_user_by_email(email)
        
        # Assert result is None
        assert result is None
        # Assert filter was called with correct email
        mock_filter.assert_called_once_with(email=email)


@pytest.mark.asyncio
async def test_authenticate_user_success():
    """Test that authenticate_user works with correct credentials"""
    email = "test@example.com"
    password = "correct_password"
    
    # Create a mock user with the correct password hash
    mock_user = AsyncMock()
    mock_user.email = email
    mock_user.enc_password = "hashed_password"
    
    # Mock finding the user
    with patch("app.utils.authentication.find_user_by_email") as mock_find:
        mock_find.return_value = mock_user
        
        # Mock password verification to return True
        with patch("app.utils.authentication.verify_password") as mock_verify:
            mock_verify.return_value = True
            
            result = await authenticate_user(email, password)
            
            # Assert result is the mock user
            assert result == mock_user
            # Assert find_user_by_email was called with correct email
            mock_find.assert_called_once_with(email)
            # Assert verify_password was called with correct args
            mock_verify.assert_called_once_with(password, mock_user.enc_password)


@pytest.mark.asyncio
async def test_authenticate_user_wrong_password():
    """Test that authenticate_user returns None with wrong password"""
    email = "test@example.com"
    password = "wrong_password"
    
    # Create a mock user
    mock_user = AsyncMock()
    mock_user.email = email
    mock_user.enc_password = "hashed_password"
    
    # Mock finding the user
    with patch("app.utils.authentication.find_user_by_email") as mock_find:
        mock_find.return_value = mock_user
        
        # Mock password verification to return False
        with patch("app.utils.authentication.verify_password") as mock_verify:
            mock_verify.return_value = False
            
            result = await authenticate_user(email, password)
            
            # Assert result is None
            assert result is None
            # Assert find_user_by_email was called with correct email
            mock_find.assert_called_once_with(email)
            # Assert verify_password was called with correct args
            mock_verify.assert_called_once_with(password, mock_user.enc_password)


@pytest.mark.asyncio
async def test_authenticate_user_not_found():
    """Test that authenticate_user returns None when user doesn't exist"""
    email = "nonexistent@example.com"
    password = "any_password"
    
    # Mock finding the user to return None
    with patch("app.utils.authentication.find_user_by_email") as mock_find:
        mock_find.return_value = None
        
        result = await authenticate_user(email, password)
        
        # Assert result is None
        assert result is None
        # Assert find_user_by_email was called with correct email
        mock_find.assert_called_once_with(email)


def test_generate_user_token():
    """Test that generating a user token works correctly"""
    # Create mock user data
    user_data = {
        "id": 1,
        "uuid": "usr_123",
        "email": "test@example.com",
        "name": "Test User",
        "status": "active",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "login_provider": "email"
    }
    expires_minutes = 60
    
    # Mock UserTokenizable validation
    mock_user_tokenizable = MagicMock()
    
    with patch("app.utils.authentication.UserTokenizable.model_validate") as mock_validate:
        mock_validate.return_value = mock_user_tokenizable
        
        # Mock generate_access_token
        expected_token = "fake.jwt.token"
        with patch("app.utils.authentication.generate_access_token") as mock_generate:
            mock_generate.return_value = expected_token
            
            result = generate_user_token(user_data, expires_minutes)
            
            # Assert result is the expected token
            assert result == expected_token
            # Assert UserTokenizable.model_validate was called with user_data
            mock_validate.assert_called_once_with(user_data)
            # Assert generate_access_token was called with correct args
            mock_generate.assert_called_once_with(
                data=mock_user_tokenizable,
                secret_key=SECRET_KEY,
                expires_minutes=expires_minutes
            )


def test_decode_user_token_valid():
    """Test that decoding a valid user token works correctly"""
    token = "fake.jwt.token"
    user_data = {
        "id": 1,
        "uuid": "usr_123",
        "email": "test@example.com"
    }
    
    # Mock decode_access_token
    with patch("app.utils.authentication.decode_access_token") as mock_decode:
        mock_decode.return_value = user_data
        
        result = decode_user_token(token)
        
        # Assert result is the user data
        assert result == user_data
        # Assert decode_access_token was called with correct args
        mock_decode.assert_called_once_with(token=token, secret_key=SECRET_KEY)


def test_decode_user_token_invalid():
    """Test that decoding an invalid user token returns None"""
    token = "invalid.jwt.token"
    
    # Mock decode_access_token to return None for invalid token
    with patch("app.utils.authentication.decode_access_token") as mock_decode:
        mock_decode.return_value = None
        
        result = decode_user_token(token)
        
        # Assert result is None
        assert result is None
        # Assert decode_access_token was called with correct args
        mock_decode.assert_called_once_with(token=token, secret_key=SECRET_KEY)


def test_random_password():
    """Test that random_password generates a string of correct length"""
    password = random_password()
    
    # Assert password is a string
    assert isinstance(password, str)
    # Assert password is 16 characters long
    assert len(password) == 16
    # Assert password contains only letters and digits
    assert all(c.isalnum() for c in password)


@pytest.mark.asyncio
async def test_persist_user_token():
    """Test that persisting a user token works correctly"""
    user_id = 1
    token = "test.jwt.token"
    expires_minutes = 60
    ip_address = "127.0.0.1"
    user_agent = "Mozilla/5.0"
    location = {"country": "US", "city": "New York"}
    device = {"type": "desktop", "os": "MacOS"}
    
    # Create mock Token instance
    mock_token = AsyncMock()
    mock_token.save = AsyncMock()
    mock_token.cache_token = AsyncMock(return_value=True)
    
    # Mock Token constructor
    with patch("app.utils.authentication.Token") as mock_token_class:
        mock_token_class.return_value = mock_token
        
        # Mock DateTime.utc to return a fixed date
        current_time = datetime.now()
        with patch("app.utils.authentication.DateTime.utc", return_value=current_time):
            # Mock TokenSchema
            expected_schema = MagicMock()
            with patch("app.utils.authentication.TokenSchema.model_validate") as mock_validate:
                mock_validate.return_value = expected_schema
                
                result = await persist_user_token(
                    user_id=user_id,
                    token=token,
                    expires_minutes=expires_minutes,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    location=location,
                    device=device
                )
                
                # Assert result is the expected schema
                assert result == expected_schema
                
                # Assert Token was created with correct args
                mock_token_class.assert_called_once()
                token_args = mock_token_class.call_args.kwargs
                assert token_args["user_id"] == user_id
                assert token_args["token"] == token
                assert token_args["ip_address"] == ip_address
                assert token_args["user_agent"] == user_agent
                assert token_args["location"] == location
                assert token_args["device"] == device
                
                # Assert token.save was called
                mock_token.save.assert_called_once()
                
                # Assert token.cache_token was called with correct args
                mock_token.cache_token.assert_called_once_with(expires_minutes=expires_minutes)
                
                # Assert TokenSchema.model_validate was called with the token
                mock_validate.assert_called_once_with(mock_token)


@pytest.mark.asyncio
async def test_login_user_with_password_success():
    """Test that login with password works with valid credentials"""
    email = "test@example.com"
    password = "valid_password"
    ip_address = "127.0.0.1"
    user_agent = "Mozilla/5.0"
    expires_minutes = 60
    token = "test.jwt.token"
    
    # Create a mock user with active status
    mock_user = AsyncMock()
    mock_user.id = 1
    mock_user.email = email
    mock_user.status = UserStatus.active
    mock_user.to_dict.return_value = {"id": 1, "email": email, "status": "active"}
    
    # Mock authenticate_user to return the mock user
    with patch("app.utils.authentication.authenticate_user") as mock_auth:
        mock_auth.return_value = mock_user
        
        # Mock generate_user_token
        with patch("app.utils.authentication.generate_user_token") as mock_generate:
            mock_generate.return_value = token
            
            # Mock persist_user_token
            with patch("app.utils.authentication.persist_user_token") as mock_persist:
                mock_persist.return_value = MagicMock()
                
                result = await login_user_with_password(
                    email=email,
                    password=password,
                    expires_minutes=expires_minutes,
                    ip_address=ip_address,
                    user_agent=user_agent
                )
                
                # Assert result is the token
                assert result == token
                
                # Assert authenticate_user was called with correct args
                mock_auth.assert_called_once_with(email, password)
                
                # Assert generate_user_token was called with correct args
                mock_generate.assert_called_once_with(mock_user.to_dict.return_value, expires_minutes)
                
                # Assert persist_user_token was called with correct args
                mock_persist.assert_called_once_with(
                    mock_user.id, token, expires_minutes, ip_address, user_agent, None, None
                )


@pytest.mark.asyncio
async def test_login_user_with_password_inactive_user():
    """Test that login with password raises an exception for inactive users"""
    email = "inactive@example.com"
    password = "valid_password"
    
    # Create a mock user with inactive status
    mock_user = AsyncMock()
    mock_user.id = 2
    mock_user.email = email
    mock_user.status = UserStatus.inactive
    
    # Mock authenticate_user to return the mock user
    with patch("app.utils.authentication.authenticate_user") as mock_auth:
        mock_auth.return_value = mock_user
        
        # Assert that an HTTPException is raised
        with pytest.raises(HTTPException) as exc_info:
            await login_user_with_password(email=email, password=password)
        
        # Check the exception details
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "User is not active"
        
        # Assert authenticate_user was called with correct args
        mock_auth.assert_called_once_with(email, password)


@pytest.mark.asyncio
async def test_login_user_with_password_invalid_credentials():
    """Test that login with password returns None for invalid credentials"""
    email = "test@example.com"
    password = "invalid_password"
    
    # Mock authenticate_user to return None (invalid credentials)
    with patch("app.utils.authentication.authenticate_user") as mock_auth:
        mock_auth.return_value = None
        
        result = await login_user_with_password(email=email, password=password)
        
        # Assert result is None
        assert result is None
        
        # Assert authenticate_user was called with correct args
        mock_auth.assert_called_once_with(email, password)


@pytest.mark.asyncio
async def test_get_current_user_oauth_token():
    """Test that get_current_user works with valid OAuth token"""
    oauth_token = "valid.oauth.token"
    user_data = {
        "id": 1,
        "uuid": "usr_123",
        "email": "test@example.com",
        "status": "active"
    }
    
    # Mock decode_user_token to return valid data for OAuth token
    with patch("app.utils.authentication.decode_user_token") as mock_decode:
        mock_decode.side_effect = [user_data, None]  # First call returns data, second call returns None
        
        # Mock UserTokenizable validation
        expected_user = MagicMock()
        with patch("app.utils.authentication.UserTokenizable.model_validate") as mock_validate:
            mock_validate.return_value = expected_user
            
            # Create mock bearer token that won't be used
            mock_bearer = MagicMock()
            mock_bearer.credentials = "bearer.token"
            
            result = await get_current_user(oauth_token=oauth_token, bearer_token=mock_bearer)
            
            # Assert result is the expected user
            assert result == expected_user
            
            # Assert decode_user_token was called with OAuth token
            mock_decode.assert_called_once_with(oauth_token)
            
            # Assert UserTokenizable.model_validate was called with user data
            mock_validate.assert_called_once_with(user_data)


@pytest.mark.asyncio
async def test_get_current_user_bearer_token():
    """Test that get_current_user works with valid bearer token when OAuth fails"""
    oauth_token = "invalid.oauth.token"
    bearer_token_value = "valid.bearer.token"
    user_data = {
        "id": 1,
        "uuid": "usr_123",
        "email": "test@example.com",
        "status": "active"
    }
    
    # Mock decode_user_token to return None for OAuth token but valid data for bearer token
    with patch("app.utils.authentication.decode_user_token") as mock_decode:
        mock_decode.side_effect = [None, user_data]  # First call returns None, second call returns data
        
        # Mock UserTokenizable validation
        expected_user = MagicMock()
        with patch("app.utils.authentication.UserTokenizable.model_validate") as mock_validate:
            mock_validate.return_value = expected_user
            
            # Create mock bearer token
            mock_bearer = MagicMock()
            mock_bearer.credentials = bearer_token_value
            
            result = await get_current_user(oauth_token=oauth_token, bearer_token=mock_bearer)
            
            # Assert result is the expected user
            assert result == expected_user
            
            # Assert decode_user_token was called with both tokens
            assert mock_decode.call_count == 2
            mock_decode.assert_any_call(oauth_token)
            mock_decode.assert_any_call(bearer_token_value)
            
            # Assert UserTokenizable.model_validate was called with user data
            mock_validate.assert_called_once_with(user_data)


@pytest.mark.asyncio
async def test_get_current_user_both_tokens_invalid():
    """Test that get_current_user raises an exception when both tokens are invalid"""
    oauth_token = "invalid.oauth.token"
    bearer_token_value = "invalid.bearer.token"
    
    # Mock decode_user_token to return None for both tokens
    with patch("app.utils.authentication.decode_user_token") as mock_decode:
        mock_decode.return_value = None
        
        # Create mock bearer token
        mock_bearer = MagicMock()
        mock_bearer.credentials = bearer_token_value
        
        # Assert that an HTTPException is raised
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(oauth_token=oauth_token, bearer_token=mock_bearer)
        
        # Check the exception details
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid authentication credentials"
        
        # Assert decode_user_token was called with both tokens
        assert mock_decode.call_count == 2
        mock_decode.assert_any_call(oauth_token)
        mock_decode.assert_any_call(bearer_token_value)
