import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.settings import get_settings

settings = get_settings()

def get_redis_url():
  username = settings.fetch("REDIS_USERNAME", None)
  password = settings.fetch("REDIS_PASSWORD", None)
  host = settings.fetch("REDIS_HOST", "localhost")
  port = settings.fetch("REDIS_PORT", 6379)
  db = settings.fetch("REDIS_DB", 1)
  if username and password:
    database_url = f"redis://{username}:{password}@{host}:{port}/{db}"
  else:
    database_url = f"redis://{host}:{port}/{db}"
  return database_url

print(get_redis_url())
