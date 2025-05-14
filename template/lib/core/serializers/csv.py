from datetime import datetime, date
import csv
from io import StringIO
from typing import Any, Dict, List

def _dict_to_csv(data: Dict[str, Any]) -> str:
    """Convert a dictionary to CSV string."""
    if not data:
        return ""
    
    # Create a string buffer to write CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow(data.keys())
    # Write values
    writer.writerow(data.values())
    
    return output.getvalue()

def serialize_csv(obj: Dict[str, Any]) -> str:
    """Serialize a dictionary to CSV string."""
    return _dict_to_csv(obj)

def deserialize_csv(csv_str: str) -> Dict[str, Any]:
    """Deserialize a CSV string to a dictionary."""
    if not csv_str.strip():
        return {}
    
    # Create a string buffer to read CSV
    input_buffer = StringIO(csv_str)
    reader = csv.reader(input_buffer)
    
    # Read header and values
    try:
        header = next(reader)
        values = next(reader)
        return dict(zip(header, values))
    except StopIteration:
        return {} 