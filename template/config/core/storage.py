from typing import Annotated
from fastapi import Depends
from functools import lru_cache

from lib.core.env import APP_ENV
from config.core.settings import decode_yaml
from lib.core.storage import Storage

# Load and parse storage configuration once, based on the environment
storage_config = decode_yaml("config/storage.yml")[APP_ENV]

# Dependency injection function for FastAPI
@lru_cache()
def get_storage() -> Storage:
  return Storage(storage_config)

# Type alias for injecting Storage via FastAPI's dependency system
StorageDep = Annotated[Storage, Depends(get_storage)]
