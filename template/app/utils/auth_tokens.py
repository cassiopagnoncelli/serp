from typing import Optional
import logging

from config.core.settings import get_settings
from config.core.redis_manager import RedisManager
from lib.core.serializers.bytecode import serialize_bytecode, deserialize_bytecode

logger = logging.getLogger(__name__)

settings = get_settings()

TOKEN_CACHE_PREFIX: str = "token:"

async def store_token(
  token: str,
  token_data: dict,
  expires_minutes: int = settings.fetch("ACCESS_TOKEN_EXPIRE_MINUTES")
) -> bool:
    if settings.fetch("CACHE_TOKENS") != "true":
        return True
    try:
        async with RedisManager.redis() as client:
            serialized_data = serialize_bytecode(token_data)
            await client.set(
                f"{TOKEN_CACHE_PREFIX}{token}",
                serialized_data,
                ex=expires_minutes * 60
            )
            return True
    except Exception as e:
        logger.error(f"Failed to cache token: {str(e)}")
        return False

async def get_cached_token(token: str) -> Optional[dict]:
    if settings.fetch("CACHE_TOKENS") != "true":
        return {}
    try:
        async with RedisManager.redis() as client:
            token_data = await client.get(f"{TOKEN_CACHE_PREFIX}{token}")
            if token_data:
                return deserialize_bytecode(token_data)
            return None
    except Exception as e:
        logger.error(f"Failed to get cached token: {str(e)}")
        return None

async def delete_cached_token(token: str) -> bool:
    if settings.fetch("CACHE_TOKENS") != "true":
        return True
    try:
        async with RedisManager.redis() as client:
            await client.delete(f"{TOKEN_CACHE_PREFIX}{token}")
            return True
    except Exception as e:
        logger.error(f"Failed to delete cached token: {str(e)}")
        return False

async def refresh_cached_token(
  token: str,
  expires_minutes: int = settings.fetch("ACCESS_TOKEN_EXPIRE_MINUTES")
) -> bool:
    if settings.fetch("CACHE_TOKENS") != "true":
        return True
    try:
        async with RedisManager.redis() as client:
            await client.expire(
                f"{TOKEN_CACHE_PREFIX}{token}",
                expires_minutes * 60
            )
            return True
    except Exception as e:
        logger.error(f"Failed to refresh cached token: {str(e)}")
        return False
