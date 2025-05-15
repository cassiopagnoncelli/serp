import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock

from app.utils.auth_tokens import (
    store_token,
    get_cached_token,
    delete_cached_token,
    refresh_cached_token,
    TOKEN_CACHE_PREFIX
)
from lib.core.serializers.bytecode import serialize_bytecode, deserialize_bytecode


@pytest.mark.asyncio
async def test_store_token_success():
    """Test that storing a token works correctly"""
    token = "test-token-123"
    token_data = {"user_id": 1, "expires": "2023-01-01"}
    expires_minutes = 30
    
    # Mock Redis client
    redis_mock = AsyncMock()
    redis_mock.set.return_value = True
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            result = await store_token(token, token_data, expires_minutes)
            
            # Assert the function returned True
            assert result is True
            
            # Assert Redis.set was called with correct parameters
            redis_mock.set.assert_called_once()
            args, kwargs = redis_mock.set.call_args
            
            # Check that key is correct
            assert args[0] == f"{TOKEN_CACHE_PREFIX}{token}"
            
            # Check that value was properly serialized
            serialized_data = serialize_bytecode(token_data)
            assert args[1] == serialized_data
            
            # Check that expiry was set correctly
            assert kwargs["ex"] == expires_minutes * 60


@pytest.mark.asyncio
async def test_store_token_caching_disabled():
    """Test that store_token returns True when caching is disabled"""
    token = "test-token-123"
    token_data = {"user_id": 1, "expires": "2023-01-01"}
    
    # Mock settings to disable token caching
    with patch("app.utils.auth_tokens.settings.fetch", return_value="false"):
        # Mock RedisManager to ensure it's not called
        with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
            result = await store_token(token, token_data)
            
            # Assert the function returned True
            assert result is True
            
            # Assert Redis was not accessed
            redis_manager_mock.assert_not_called()


@pytest.mark.asyncio
async def test_store_token_exception():
    """Test that store_token handles exceptions"""
    token = "test-token-123"
    token_data = {"user_id": 1, "expires": "2023-01-01"}
    
    # Mock Redis client to raise an exception
    redis_mock = AsyncMock()
    redis_mock.set.side_effect = Exception("Redis connection error")
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            # Mock logger to prevent actual logging during test
            with patch("app.utils.auth_tokens.logger.error"):
                result = await store_token(token, token_data)
                
                # Assert the function returned False
                assert result is False


@pytest.mark.asyncio
async def test_get_cached_token_success():
    """Test that retrieving a cached token works correctly"""
    token = "test-token-123"
    token_data = {"user_id": 1, "expires": "2023-01-01"}
    serialized_data = serialize_bytecode(token_data)
    
    # Mock Redis client
    redis_mock = AsyncMock()
    redis_mock.get.return_value = serialized_data
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            result = await get_cached_token(token)
            
            # Assert the result is deserialized correctly
            assert result == token_data
            
            # Assert Redis.get was called with correct key
            redis_mock.get.assert_called_once_with(f"{TOKEN_CACHE_PREFIX}{token}")


@pytest.mark.asyncio
async def test_get_cached_token_not_found():
    """Test that get_cached_token returns None when token is not found"""
    token = "nonexistent-token"
    
    # Mock Redis client
    redis_mock = AsyncMock()
    redis_mock.get.return_value = None
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            result = await get_cached_token(token)
            
            # Assert the result is None
            assert result is None


@pytest.mark.asyncio
async def test_get_cached_token_caching_disabled():
    """Test that get_cached_token returns empty dict when caching is disabled"""
    token = "test-token-123"
    
    # Mock settings to disable token caching
    with patch("app.utils.auth_tokens.settings.fetch", return_value="false"):
        # Mock RedisManager to ensure it's not called
        with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
            result = await get_cached_token(token)
            
            # Assert the function returned empty dict
            assert result == {}
            
            # Assert Redis was not accessed
            redis_manager_mock.assert_not_called()


@pytest.mark.asyncio
async def test_get_cached_token_exception():
    """Test that get_cached_token handles exceptions"""
    token = "test-token-123"
    
    # Mock Redis client to raise an exception
    redis_mock = AsyncMock()
    redis_mock.get.side_effect = Exception("Redis connection error")
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            # Mock logger to prevent actual logging during test
            with patch("app.utils.auth_tokens.logger.error"):
                result = await get_cached_token(token)
                
                # Assert the function returned None
                assert result is None


@pytest.mark.asyncio
async def test_delete_cached_token_success():
    """Test that deleting a token works correctly"""
    token = "test-token-123"
    
    # Mock Redis client
    redis_mock = AsyncMock()
    redis_mock.delete.return_value = 1
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            result = await delete_cached_token(token)
            
            # Assert the function returned True
            assert result is True
            
            # Assert Redis.delete was called with correct key
            redis_mock.delete.assert_called_once_with(f"{TOKEN_CACHE_PREFIX}{token}")


@pytest.mark.asyncio
async def test_delete_cached_token_caching_disabled():
    """Test that delete_cached_token returns True when caching is disabled"""
    token = "test-token-123"
    
    # Mock settings to disable token caching
    with patch("app.utils.auth_tokens.settings.fetch", return_value="false"):
        # Mock RedisManager to ensure it's not called
        with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
            result = await delete_cached_token(token)
            
            # Assert the function returned True
            assert result is True
            
            # Assert Redis was not accessed
            redis_manager_mock.assert_not_called()


@pytest.mark.asyncio
async def test_delete_cached_token_exception():
    """Test that delete_cached_token handles exceptions"""
    token = "test-token-123"
    
    # Mock Redis client to raise an exception
    redis_mock = AsyncMock()
    redis_mock.delete.side_effect = Exception("Redis connection error")
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            # Mock logger to prevent actual logging during test
            with patch("app.utils.auth_tokens.logger.error"):
                result = await delete_cached_token(token)
                
                # Assert the function returned False
                assert result is False


@pytest.mark.asyncio
async def test_refresh_cached_token_success():
    """Test that refreshing a token works correctly"""
    token = "test-token-123"
    expires_minutes = 60
    
    # Mock Redis client
    redis_mock = AsyncMock()
    redis_mock.expire.return_value = 1
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            result = await refresh_cached_token(token, expires_minutes)
            
            # Assert the function returned True
            assert result is True
            
            # Assert Redis.expire was called with correct parameters
            redis_mock.expire.assert_called_once_with(
                f"{TOKEN_CACHE_PREFIX}{token}",
                expires_minutes * 60
            )


@pytest.mark.asyncio
async def test_refresh_cached_token_caching_disabled():
    """Test that refresh_cached_token returns True when caching is disabled"""
    token = "test-token-123"
    
    # Mock settings to disable token caching
    with patch("app.utils.auth_tokens.settings.fetch", return_value="false"):
        # Mock RedisManager to ensure it's not called
        with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
            result = await refresh_cached_token(token)
            
            # Assert the function returned True
            assert result is True
            
            # Assert Redis was not accessed
            redis_manager_mock.assert_not_called()


@pytest.mark.asyncio
async def test_refresh_cached_token_exception():
    """Test that refresh_cached_token handles exceptions"""
    token = "test-token-123"
    
    # Mock Redis client to raise an exception
    redis_mock = AsyncMock()
    redis_mock.expire.side_effect = Exception("Redis connection error")
    
    # Mock RedisManager to return our mocked redis client
    with patch("app.utils.auth_tokens.RedisManager.redis") as redis_manager_mock:
        redis_manager_mock.return_value.__aenter__.return_value = redis_mock
        redis_manager_mock.return_value.__aexit__.return_value = None
        
        # Mock settings to enable token caching
        with patch("app.utils.auth_tokens.settings.fetch", return_value="true"):
            # Mock logger to prevent actual logging during test
            with patch("app.utils.auth_tokens.logger.error"):
                result = await refresh_cached_token(token)
                
                # Assert the function returned False
                assert result is False
