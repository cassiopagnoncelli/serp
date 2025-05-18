import redis.asyncio as redis
from typing import Optional, Any
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class AsyncRedisClient:
    """
    Async Redis client manager that provides easy access to Redis clients.
    Supports connection pooling and proper cleanup.
    """
    
    def __init__(
        self,
        url: str,
        max_connections: int = 10,
        decode_responses: bool = True,
        socket_connect_timeout: int = 10,  # Default 10 seconds
        socket_timeout: int = 10,  # Default 10 seconds
        **kwargs
    ):
        """
        Initialize AsyncRedisClient
        
        Args:
            url: Redis connection URL from settings
            max_connections: Maximum number of connections in the pool
            decode_responses: Whether to decode responses to strings
            socket_connect_timeout: Timeout for socket connection in seconds
            socket_timeout: Timeout for socket operations in seconds
            **kwargs: Additional Redis connection parameters
        """
        self.url = url
        self.max_connections = max_connections
        self.decode_responses = decode_responses
        self.socket_connect_timeout = socket_connect_timeout
        self.socket_timeout = socket_timeout
        self.kwargs = kwargs
        self._client: Optional[redis.Redis] = None
        self._pool: Optional[redis.ConnectionPool] = None
        self._is_connected = False
    
    async def connect(self) -> None:
        """Initialize the Redis connection and pool"""
        if self._is_connected:
            return
        
        try:
            # Create connection pool with timeouts
            connection_kwargs = {
                'socket_connect_timeout': self.socket_connect_timeout,
                'socket_timeout': self.socket_timeout,
                **self.kwargs
            }
            
            self._pool = redis.ConnectionPool.from_url(
                self.url,
                max_connections=self.max_connections,
                decode_responses=self.decode_responses,
                **connection_kwargs
            )
            
            # Create Redis client using the pool
            self._client = redis.Redis(connection_pool=self._pool)
            
            # Test the connection
            await self._client.ping()
            self._is_connected = True
            logger.info(f"Connected to Redis at {self.url}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            await self.disconnect()
            raise
    
    async def disconnect(self) -> None:
        """Close the Redis connection and pool"""
        self._is_connected = False
        
        if self._client:
            await self._client.close()
            self._client = None
        
        if self._pool:
            await self._pool.disconnect()
            self._pool = None
        
        logger.info("Disconnected from Redis")
    
    async def get_client(self) -> redis.Redis:
        """Get the Redis client, connecting if necessary"""
        if not self._is_connected or self._client is None:
            await self.connect()
        return self._client
    
    @asynccontextmanager
    async def client(self):
        """Context manager that yields a connected Redis client"""
        client = await self.get_client()
        try:
            yield client
        finally:
            # The connection pool handles returning connections
            pass
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.disconnect()
    
    # Convenience methods for common operations
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key"""
        client = await self.get_client()
        return await client.get(key)
    
    async def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        """Set a key-value pair with optional expiration"""
        client = await self.get_client()
        return await client.set(key, value, ex=ex)
    
    async def delete(self, *keys: str) -> int:
        """Delete one or more keys"""
        client = await self.get_client()
        return await client.delete(*keys)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists"""
        client = await self.get_client()
        return bool(await client.exists(key))
    
    async def ping(self) -> bool:
        """Ping Redis to check connection"""
        try:
            client = await self.get_client()
            await client.ping()
            return True
        except Exception:
            return False
