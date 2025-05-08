from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel

class TokenCreate(SQLModel):
  user_id: int
  token: str
  expires_at: datetime
  ip_address: Optional[str] = None
  user_agent: Optional[str] = None
  location: Optional[str] = None
  device: Optional[str] = None
