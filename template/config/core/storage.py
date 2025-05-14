from typing import Annotated
from fastapi import Depends
from functools import lru_cache
import sys
import os
from pathlib import Path

from lib.core.env import APP_ENV
from config.core.settings import decode_yaml
from lib.core.storage.main import Storage

# Load and parse storage configuration once, based on the environment
storage_config = decode_yaml("config/storage.yml")[APP_ENV]

# Dependency injection function for FastAPI
@lru_cache()
def get_storage() -> Storage:
  try:
    return Storage(storage_config)
  except Exception as e:
    # Log the error but allow the application to continue
    print(f"Warning: Failed to initialize storage: {str(e)}", file=sys.stderr)
    
    # For console applications, fallback to local storage if there's an error
    if any('console.py' in arg for arg in sys.argv):
      print("Falling back to local storage for console", file=sys.stderr)
      local_path = Path("tmp/storage")
      local_path.mkdir(parents=True, exist_ok=True)
      return Storage({
        'driver': 'local',
        'url_endpoint': str(local_path)
      })
    
    # Otherwise re-raise the exception
    raise

# Type alias for injecting Storage via FastAPI's dependency system
StorageDep = Annotated[Storage, Depends(get_storage)]
