from tortoise.models import Model
from tortoise import fields
from enum import Enum
from datetime import datetime

from lib.core.authentication.passwords import encrypt_password
from lib.core.record.uuid import generate_id

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class LoginProvider(str, Enum):
    email = "email"
    google = "google"
    facebook = "facebook"

class User(Model):
    id = fields.IntField(pk=True)
    uuid = fields.CharField(max_length=255, unique=True, index=True, default=lambda: generate_id("usr"))
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    
    # Relationships
    account_uuid = fields.CharField(max_length=255, index=True, null=True)
    
    # Email, password fields
    email = fields.CharField(max_length=255, unique=True, index=True)
    enc_password = fields.CharField(max_length=255)
    
    # User attributes
    name = fields.CharField(max_length=255, null=True)
    status = fields.CharEnumField(UserStatus, default=UserStatus.active)
    login_provider = fields.CharEnumField(LoginProvider, default=LoginProvider.email)

    class Meta:
        table = "users"
        default_connection = "default"

    async def save(self, *args, **kwargs):
        if hasattr(self, 'password'):
            self.enc_password = encrypt_password(self.password)
            delattr(self, 'password')
        await super().save(*args, **kwargs)
