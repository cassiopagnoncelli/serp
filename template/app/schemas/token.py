from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, field_validator

from lib.core.record.base import BasePydanticModel

class TokenSchema(BasePydanticModel):
  # Automatic fields
  id: int
  created_at: datetime
  updated_at: datetime
  # Relationships
  user_id: int
  # Token fields
  token: str
  expires_at: datetime
  ip_address: Optional[str] = None
  user_agent: Optional[str] = None
  location: Optional[Dict[str, Any]] = None
  device: Optional[Dict[str, Any]] = None

class CreateTokenSchema(BaseModel):
  # Relationships
  user_id: int
  # Token fields
  token: str
  expires_at: datetime
  ip_address: Optional[str] = None
  user_agent: Optional[str] = None
  location: Optional[Dict[str, Any]] = None
  device: Optional[Dict[str, Any]] = None

  @field_validator('expires_at')
  @classmethod
  def ensure_naive_datetime(cls, v: datetime) -> datetime:
    if v.tzinfo is not None:
      return v.replace(tzinfo=None)
    return v
