from typing import Annotated, Optional
import random
from datetime import datetime, UTC
from sqlmodel import Field, SQLModel
from sqlalchemy import JSON

class Token(SQLModel, table=True):
    __tablename__ = "tokens"

    # Automatic fields
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=None, index=False)
    updated_at: datetime = Field(default=None, index=False)
    # Relationships
    user_id: int = Field(default=None, index=True, unique=False)
    # Token fields
    token: str = Field(index=True, unique=True)
    expires_at: datetime = Field(index=False)
    ip_address: str = Field(index=False)
    user_agent: str = Field(index=False)
    location: dict = Field(index=False, sa_type=JSON)
    device: dict = Field(index=False, sa_type=JSON)

    def __init__(self, **data):
        timestamp = datetime.now(UTC)
        if 'created_at' not in data or data['created_at'] is None:
            data['created_at'] = timestamp
        if 'updated_at' not in data or data['updated_at'] is None:
            data['updated_at'] = timestamp
        super().__init__(**data)
