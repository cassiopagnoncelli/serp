import redis
from fastapi import FastAPI, Depends
from typing import Annotated
from config.initializers.settings import get_settings

settings = get_settings()

redis_pool = redis.ConnectionPool(url=settings.REDIS_URL, decode_responses=True)

def get_redis():
  redis_client = redis.Redis(connection_pool=redis_pool)
  try:
    yield redis_client
  finally:
    pass # No need to close the connection as it returns to the pool

# Type hint for Redis dependency injection
#
# async def read_item(item_id: str, redis: RedisClient):
#   cached_item = redis.get(f"item:{item_id}")
RedisClient = Annotated[redis.Redis, Depends(get_redis)]
