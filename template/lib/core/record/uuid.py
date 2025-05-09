import random
import string

def generate_id(prefix: str, length: int = 8):
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return f"{prefix}_{random_chars}"
