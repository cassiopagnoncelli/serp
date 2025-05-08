from typing import Optional
from sqlmodel import SQLModel

class UserPublic(SQLModel):
  uuid: str
  name: str
  email: str

class UserCreate(SQLModel):
  name: str
  email: str
  enc_password: str

class UserUpdate(SQLModel):
  name: Optional[str] = None
  email: Optional[str] = None
  enc_password: Optional[str] = None

class UserTokenizable(SQLModel):
  id: int
  uuid: str
  account_uuid: Optional[str] = None
  email: str
  name: Optional[str] = None
  status: Optional[str] = None
  login_provider: Optional[str] = None
