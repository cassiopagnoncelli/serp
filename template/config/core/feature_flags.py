from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Any, Dict
from pydantic import BaseModel, create_model

from config.core.settings import decode_yaml
from lib.core.env import APP_ENV

feature_flags_config = decode_yaml("config/feature_flags.yml")[APP_ENV]

def create_dynamic_model(data: Dict[str, Any], name: str = "DynamicModel") -> type[BaseModel]:
    """Create a dynamic Pydantic model based on the input data structure."""
    fields = {}
    for key, value in data.items():
        if isinstance(value, dict):
            fields[key] = (create_dynamic_model(value, f"{name}_{key}"), ...)
        else:
            fields[key] = (type(value), ...)
    return create_model(name, **fields)

class FeatureFlags(BaseSettings):
    def __init__(self, **data):
        # Create a dynamic model based on the current config
        DynamicFeatureFlags = create_dynamic_model(feature_flags_config)
        # Initialize with the dynamic model
        self._model = DynamicFeatureFlags(**feature_flags_config)
    
    def _get_nested_value(self, path: str) -> Any:
        """Get a value from a nested dictionary using dot notation."""
        current = self._model.dict()
        for key in path.split('.'):
            if not isinstance(current, dict):
                return None
            current = current.get(key)
            if current is None:
                return None
        return current

    def get(self, key: str) -> bool | None:
        """Get a feature flag value, supporting nested paths. Returns None if key is not found."""
        value = self._get_nested_value(key)
        if value is None:
            return None
        return bool(value)

@lru_cache()
def get_feature_flags() -> FeatureFlags:
    return FeatureFlags()
