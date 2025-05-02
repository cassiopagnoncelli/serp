from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, TypeVar, Optional

T = TypeVar('T')

class Settings(BaseSettings):
  APP_NAME: str = "bla"
  DEBUG: bool = False

  # Updated Config to the new v2 style
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=False,
    extra="allow"
  )

  def fetch(self, key: str, default: Optional[T] = None) -> Any:
    """
    Fetch a setting value, returning the default if the key doesn't exist.
    
    Args:
        key: The setting key to fetch
        default: The default value to return if the key doesn't exist
        
    Returns:
        The setting value if it exists, otherwise the default value
    """
    return getattr(self, key, default)

@lru_cache()
def get_settings() -> Settings:
    return Settings()

# How to use it:
#
# from core.settings import get_settings
#
# settings = get_settings()
#
# print(settings.APP_NAME)
# print(settings.DEBUG)
# print(settings.API_KEY)
# print(settings.fetch('NON_EXISTENT_KEY', 'default_value'))
