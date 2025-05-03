# One-liner task description
#~ secret: Generate a secure random secret

import secrets
import sys

def generate_secret():
    """Generate a secure random secret."""
    return secrets.token_hex(32)

if __name__ == "__main__":
    print(generate_secret())
