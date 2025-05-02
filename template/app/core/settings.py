from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, TypeVar, Optional
import os

T = TypeVar('T')

class Settings(BaseSettings):
  APP_NAME: str = "bla"
  DEBUG: bool = False

  # Updated Config to the new v2 style
  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    case_sensitive=True,
    extra="allow"
  )

  def fetch(self, key: str, default: Optional[T] = None) -> Any:
    """
    Fetch a setting value, trying in this order:
    1. Class attribute
    2. Environment variable
    3. Default value (or empty string if no default provided)
    
    Args:
        key: The setting key to fetch
        default: The default value to return if the key doesn't exist
        
    Returns:
        The setting value if it exists, otherwise the default value or empty string
    """
    # First try to get from class attributes
    class_value = getattr(self, key, None)
    if class_value is not None:
        return class_value
        
    # Then try to get from environment variables
    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value
        
    # Finally return default or empty string
    return default if default is not None else None

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
