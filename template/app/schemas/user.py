from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from lib.core.record.base import BasePydanticModel

class UserSchema(BasePydanticModel):
  # Automatic fields
  id: int
  uuid: str
  created_at: datetime
  updated_at: datetime
  # Relationships
  account_uuid: str
  # Email, password fields
  email: str
  enc_password: str
  # User attributes
  name: Optional[str] = None
  status: Optional[str] = None
  login_provider: Optional[str] = None

class UserPublic(BaseModel):
  uuid: str
  created_at: datetime
  updated_at: datetime
  account_uuid: Optional[str] = None
  email: str
  name: Optional[str] = None
  status: Optional[str] = None
  login_provider: Optional[str] = None

class UserCreate(BaseModel):
  email: str
  password: str
  name: Optional[str] = None

class UserUpdate(BaseModel):
  email: Optional[str] = None
  password: Optional[str] = None
  name: Optional[str] = None

class UserTokenizable(BaseModel):
  id: int
  uuid: str
  created_at: datetime
  updated_at: datetime
  account_uuid: Optional[str] = None
  email: str
  name: Optional[str] = None
  status: Optional[str] = None
  login_provider: Optional[str] = None
