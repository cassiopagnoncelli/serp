from tortoise import fields
from enum import Enum
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict

from lib.core.authentication.passwords import encrypt_password
from lib.core.record.uuid import generate_id
from lib.core.record.inflection import to_table_name
from lib.core.record.base import Base

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class LoginProvider(str, Enum):
    email = "email"
    google = "google"
    facebook = "facebook"

class User(Base):
    class Meta:
        table = to_table_name("User")

    # Primary key
    uuid = fields.CharField(max_length=255, default=lambda: generate_id("usr"), pk=False)

    # Relationships
    account_uuid = fields.CharField(max_length=255, index=True, null=True)

    # Email, password fields
    email = fields.CharField(max_length=255, unique=True, index=True)
    enc_password = fields.CharField(max_length=255)

    # User attributes
    name = fields.CharField(max_length=255, null=True)
    status = fields.CharEnumField(UserStatus, default=UserStatus.active, max_length=255)
    login_provider = fields.CharEnumField(LoginProvider, default=LoginProvider.email, max_length=255)

    # Default handlers for field transformations
    defaults = {
        "enc_password": lambda kwargs: encrypt_password(kwargs.get('password')) if 'password' in kwargs else None
    }

    async def logout(self) -> None:
        tokens = await Token.filter(user_id=self.id).all()
        for token in tokens:
            await token.destroy()

    async def destroy(self) -> None:
        await self.logout()
        await self.delete()
