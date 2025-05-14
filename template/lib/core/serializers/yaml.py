from datetime import datetime, date
import yaml
from typing import Any, Dict
from enum import Enum

def _to_primitive(value: Any) -> Any:
    """Convert non-primitive types to primitive values."""
    if isinstance(value, Enum):
        return value.value
    elif isinstance(value, (datetime, date)):
        return value.isoformat()
    elif isinstance(value, dict):
        return {k: _to_primitive(v) for k, v in value.items()}
    elif isinstance(value, list):
        return [_to_primitive(item) for item in value]
    return value

def _dict_to_yaml(data: Dict[str, Any]) -> str:
    """Convert a dictionary to YAML string."""
    # Convert all values to primitive types
    primitive_data = _to_primitive(data)
    return yaml.dump(primitive_data, default_flow_style=False, allow_unicode=True)

def serialize_yaml(obj: Dict[str, Any]) -> str:
    """Serialize a dictionary to YAML string."""
    return _dict_to_yaml(obj)

def deserialize_yaml(yaml_str: str) -> Dict[str, Any]:
    """Deserialize a YAML string to a dictionary."""
    # Use safe_load to prevent arbitrary code execution
    # and handle Python objects as plain dictionaries
    return yaml.safe_load(yaml_str)
