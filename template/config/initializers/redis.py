import redis
from fastapi import Depends
from typing import Annotated
from contextlib import contextmanager
from config.initializers.settings import get_settings

settings = get_settings()

redis_pool = redis.ConnectionPool(
  url = settings.fetch("REDIS_URL"),
  decode_responses = True
)

def get_redis():
  redis_client = redis.Redis(connection_pool=redis_pool)
  try:
    yield redis_client
  finally:
    pass  # No need to close the connection as it returns to the pool

RedisClient = Annotated[redis.Redis, Depends(get_redis)]

@contextmanager
def get_redis_standalone():
  with redis.Redis(connection_pool=redis_pool) as redis_client:
    yield redis_client

# Example usage in FastAPI:
#
#   @app.get("/users")
#   def get_users(redis: RedisClient):
#     redis.get("item:1")
#
# For general-purpose usage:
#
#   with get_redis_standalone() as redis_client:
#     redis_client.get("item:1")
