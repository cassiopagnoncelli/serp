from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, TypeVar, Optional
import os

from lib.core.env import APP_ENV

T = TypeVar('T')

class Settings(BaseSettings):
  APP_NAME: str = "my_app_development"
  DEBUG: bool = False

  model_config = SettingsConfigDict(
    env_file = f".env.{APP_ENV}",
    env_file_encoding = "utf-8",
    case_sensitive = True,
    extra = "allow"
  )

  def fetch(self, key: str, default: Optional[T] = None) -> Any:
    class_value = getattr(self, key, None)
    if class_value is not None:
        return class_value

    env_value = os.environ.get(key)
    if env_value is not None:
        return env_value

    return default if default is not None else None

@lru_cache()
def get_settings() -> Settings:
  return Settings()
