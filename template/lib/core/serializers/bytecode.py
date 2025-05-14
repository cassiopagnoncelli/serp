import base64
from dill import dumps, loads

def serialize_bytecode(obj):
    """Serialize an object using the bytecode protocol."""
    return base64.b64encode(dumps(obj)).decode('ascii')

def deserialize_bytecode(obj):
    """Deserialize an object using the bytecode protocol."""
    return loads(base64.b64decode(obj))
