import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from config.core.settings import get_settings

settings = get_settings()

print(settings.fetch("REDIS_URL", "redis://localhost:6379/0"))
