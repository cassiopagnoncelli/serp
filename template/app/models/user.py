from typing import Annotated, Optional
import random
import string
from datetime import datetime
from sqlmodel import Field, SQLModel

def generate_id(prefix: str, length: int = 16):
  random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
  return f"{prefix}_{random_chars}"

class User(SQLModel, table=True):
  __tablename__ = "users"
  id: Optional[int] = Field(default=None, primary_key=True)
  uuid: Annotated[str, Field(default_factory=lambda: generate_id("usr"), index=True, unique=True)]
  created_at: datetime = Field(index=False)
  updated_at: datetime = Field(index=False)
  email: str = Field(index=True, unique=True)
  enc_password: str = Field(index=False)
  name: Optional[str] = Field(index=False)
  status: Optional[str] = Field(index=False)
  login_provider: Optional[str] = Field(index=False)
