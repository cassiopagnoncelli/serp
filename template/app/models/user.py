from typing import Annotated, Optional
import random
import string
from sqlmodel import Field, SQLModel

def generate_id(prefix: str, length: int = 16):
  random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
  return f"{prefix}_{random_chars}"

class User(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  uuid: Annotated[str, Field(default_factory=lambda: generate_id("usr"), index=True, unique=True)]
  email: str = Field(index=True, unique=True)
  password: str = Field(index=False)
  name: str = Field(index=False)
