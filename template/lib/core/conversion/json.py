from datetime import datetime, date

def serialize_recursive(obj):
    """
    Recursively serialize a dictionary, converting all datetime and date objects to ISO format.
    Handles nested dictionaries and lists.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: serialize_recursive(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [serialize_recursive(item) for item in obj]
    return obj
