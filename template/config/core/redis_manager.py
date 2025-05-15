from lib.core.redis_service.redis_manager import RedisManager
from config.core.settings import get_settings

settings = get_settings()

RedisManager.initialize(url=settings.fetch("REDIS_URL"))

__all__ = ['RedisManager']
