import os
from os import environ
from io import StringIO
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any, TypeVar, Optional
from jinja2 import Environment, FileSystemLoader
from ruamel.yaml import YAML
from lib.core.env import *

def decode_yaml(path: str) -> dict:
  env = Environment(loader = FileSystemLoader("."), autoescape = False)
  template = env.get_template(path)
  rendered = template.render(environ)
  return YAML(typ = "safe").load(StringIO(rendered))

def dig(d, path, default = None, sep = "."):
  keys = path.split(sep)
  for key in keys:
    if isinstance(d, dict):
      d = d.get(key, default)
    else:
      return default
  return d

storage_config = decode_yaml("config/storage.yml")[APP_ENV]
database_config = decode_yaml("config/database.yml")[APP_ENV]
broker_config = decode_yaml("config/broker.yml")[APP_ENV]
redis_config = decode_yaml("config/redis.yml")[APP_ENV]

T = TypeVar('T')
class Settings(BaseSettings):
  APP_NAME: str = "my_app"
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
