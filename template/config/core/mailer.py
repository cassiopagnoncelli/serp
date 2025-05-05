from typing import Annotated
from fastapi import Depends
from functools import lru_cache

from lib.core.env import APP_ENV
from config.core.settings import decode_yaml
from lib.core.mailer import Mailer

# Load and parse storage configuration once, based on the environment
mailer_config = decode_yaml("config/mailer.yml")[APP_ENV]

# Dependency injection function for FastAPI
def get_mailer() -> Mailer:
  return Mailer(config = mailer_config, verbose = True)

# Type alias for injecting Storage via FastAPI's dependency system
MailerDep = Annotated[Mailer, Depends(get_mailer)]
