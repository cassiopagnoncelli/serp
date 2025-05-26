from redis import Redis, ConnectionPool
from fastapi import Depends
from typing import Annotated
from contextlib import contextmanager

from config.core.settings import get_settings

settings = get_settings()

redis_pool = ConnectionPool.from_url(
    url=settings.fetch("REDIS_URL"),
    decode_responses=True
)

def get_redis():
  redis_client = Redis(connection_pool=redis_pool)
  try:
    yield redis_client
  finally:
    pass  # No need to close the connection as it returns to the pool

RedisDep = Annotated[Redis, Depends(get_redis)]
