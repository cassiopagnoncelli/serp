from datetime import datetime, date
from json import dumps, loads

def replace_values_with_primitive_types(obj):
    """
    Recursively serialize a dictionary, converting all datetime and date objects to ISO format.
    Handles nested dictionaries and lists.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: replace_values_with_primitive_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_values_with_primitive_types(item) for item in obj]
    return obj

def serialize_json(obj):
    """Serialize an object to a JSON string."""
    normalized = replace_values_with_primitive_types(obj)
    return dumps(normalized)

def deserialize_json(json_str):
    """
    Deserialize a JSON string into a dictionary, converting all ISO formatted datetime and date strings back to datetime and date objects.
    """
    return loads(json_str)
