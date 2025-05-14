from dill import dumps, loads

def serialize_bytecode(obj):
    """Serialize an object using the bytecode protocol."""
    return dumps(obj)

def deserialize_bytecode(obj):
    """Deserialize an object using the bytecode protocol."""
    return loads(obj)
