from typing import Annotated, Optional
import random
import string
from datetime import datetime, UTC
from sqlmodel import Field, SQLModel

from lib.core.authentication.passwords import encrypt_password
from lib.core.record.uuid import generate_id

class User(SQLModel, table=True):
    __tablename__ = "users"

    # Automatic fields
    id: Optional[int] = Field(default=None, primary_key=True)
    uuid: Annotated[str, Field(default_factory=lambda: generate_id("usr"), index=True, unique=True)]
    created_at: datetime = Field(default=None, index=False)
    updated_at: datetime = Field(default=None, index=False)
    # Relationships
    account_uuid: str = Field(default=None, index=True, unique=False)
    # Email, password fields
    email: str = Field(index=True, unique=True)
    enc_password: str = Field(index=False)
    # User attributes
    name: Optional[str] = Field(index=False)
    status: Optional[str] = Field(index=False)
    login_provider: Optional[str] = Field(index=False)

    def __init__(self, **data):
        timestamp = datetime.now(UTC)
        if 'created_at' not in data or data['created_at'] is None:
            data['created_at'] = timestamp
        if 'updated_at' not in data or data['updated_at'] is None:
            data['updated_at'] = timestamp
        if 'password' in data:
            data['enc_password'] = encrypt_password(data.pop('password'))
            
        super().__init__(**data)
