from functools import lru_cache
from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "my-app"
    DEBUG: bool = False
    API_KEY: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

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
