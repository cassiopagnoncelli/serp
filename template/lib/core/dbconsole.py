import sys
import os

# Add the project root directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from app.core.settings import get_settings

settings = get_settings()

def get_postgresql_url():
  if settings.fetch("DATABASE_URL"):
    return settings.fetch("DATABASE_URL")
  else:
    username = settings.fetch("DB_USERNAME")
    password = settings.fetch("DB_PASSWORD")
    host = settings.fetch("DB_HOST", "localhost")
    port = settings.fetch("DB_PORT", 5432)
    name = settings.fetch("DB_NAME", f"{settings.APP_NAME}_{settings.fetch("APP_ENV", "development")}")
    database_url = f"postgresql://{username}:{password}@{host}:{port}/{name}"
    return database_url

print(get_postgresql_url())
