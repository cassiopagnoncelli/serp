import asyncio
import redis.asyncio as redis
from redis.asyncio import Redis
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager

from config.core.settings import get_settings
from lib.core.redis_service.async_redis_client import AsyncRedisClient

# RedisManager with settings integration
class RedisManager:
    """Redis manager that uses settings.fetch for configuration"""
    
    _instance: Optional[AsyncRedisClient] = None
    url: Optional[str] = None
    
    @classmethod
    def initialize(cls, url: str):
        """Initialize RedisManager with settings module"""
        cls.url = url
    
    @classmethod
    async def get_client(cls, **kwargs) -> AsyncRedisClient:
        """
        Get the Redis client instance using settings
        
        Args:
            **kwargs: Additional Redis connection parameters
        """
        if cls._instance is None:
            if cls.url is None:
                raise RuntimeError("RedisManager not initialized. Call RedisManager.initialize(url) first.")
            
            if not cls.url:
                raise ValueError("REDIS_URL not found in settings")
            
            cls._instance = AsyncRedisClient(url=cls.url, **kwargs)
        
        return cls._instance
    
    @classmethod
    async def disconnect(cls) -> None:
        """Disconnect the Redis instance"""
        if cls._instance:
            await cls._instance.disconnect()
            cls._instance = None
    
    @classmethod
    @asynccontextmanager
    async def redis(cls, **kwargs):
        """Context manager for getting a Redis client"""
        client = await cls.get_client(**kwargs)
        async with client.client() as redis_client:
            yield redis_client
    
    @classmethod
    async def get_redis_client(cls, **kwargs) -> Redis:
        """Direct access to the underlying Redis client"""
        client = await cls.get_client(**kwargs)
        return await client.get_client()
