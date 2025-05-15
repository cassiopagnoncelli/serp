import asyncio
from lib.core.redis_service.redis_manager import RedisManager

# This adapter is intended to be used in the console only.
class SyncRedisAdapter:
  """Synchronous adapter for the async RedisManager for use in the console"""
  
  def __init__(self):
    self.loop = asyncio.new_event_loop()
    
  def _run_async(self, coro):
    """Run a coroutine in the event loop"""
    return self.loop.run_until_complete(coro)
    
  def get(self, key):
    """Get a value by key"""
    async def _get():
      async with RedisManager.redis() as client:
        return await client.get(key)
    return self._run_async(_get())
    
  def set(self, key, value, ex=None):
    """Set a key-value pair with optional expiration"""
    async def _set():
      async with RedisManager.redis() as client:
        return await client.set(key, value, ex=ex)
    return self._run_async(_set())
    
  def delete(self, *keys):
    """Delete one or more keys"""
    async def _delete():
      async with RedisManager.redis() as client:
        return await client.delete(*keys)
    return self._run_async(_delete())
    
  def exists(self, key):
    """Check if a key exists"""
    async def _exists():
      async with RedisManager.redis() as client:
        return await client.exists(key)
    return self._run_async(_exists())
    
  def ping(self):
    """Ping Redis to check connection"""
    async def _ping():
      async with RedisManager.redis() as client:
        return await client.ping()
    return self._run_async(_ping())
    
  def execute_command(self, *args, **kwargs):
    """Execute a raw Redis command"""
    async def _execute():
      async with RedisManager.redis() as client:
        return await client.execute_command(*args, **kwargs)
    return self._run_async(_execute())
    
  def __getattr__(self, name):
    """Handle other Redis commands dynamically"""
    def method(*args, **kwargs):
      async def _command():
        async with RedisManager.redis() as client:
          func = getattr(client, name)
          return await func(*args, **kwargs)
      return self._run_async(_command())
    return method
