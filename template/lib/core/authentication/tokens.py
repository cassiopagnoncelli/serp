from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import PyJWTError

from lib.core.serializers.bytecode import *

ALGORITHM: str = "HS256"

def generate_access_token(data: dict, secret_key: str, expires_minutes: int) -> str:
    access_token_expires = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    content = {
        "data": str(serialize_bytecode(data)),
        "exp": access_token_expires.timestamp()
    }
    access_token = jwt.encode(content, secret_key, algorithm=ALGORITHM)

    return access_token

def decode_access_token(token: str, secret_key: str) -> dict:
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        return deserialize_bytecode(bytes(payload["data"]))
    except PyJWTError:
        return None
