from typing import Optional
from sqlmodel import SQLModel

class UserPublic(SQLModel):
  name: str
  email: str

class UserCreate(SQLModel):
  name: str
  email: str
  password: str

class UserUpdate(SQLModel):
  name: Optional[str] = None
  email: Optional[str] = None
  password: Optional[str] = None
