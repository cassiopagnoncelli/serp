from pydantic_settings import BaseSettings
from functools import lru_cache

class FeatureFlags(BaseSettings):
  # Application general settings.
  CREATE_USER_ON_GOOGLE_LOGIN: bool = True

  def get(self, key: str) -> bool:
    return getattr(self, key)

@lru_cache()
def get_feature_flags() -> FeatureFlags:
  return FeatureFlags()
