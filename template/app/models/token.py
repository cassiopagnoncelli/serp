from tortoise import fields
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict

from lib.core.record.inflection import to_table_name
from lib.core.record.base import Base
from lib.core.dt import DateTime
from app.utils.auth_tokens import store_token, delete_cached_token, refresh_cached_token
from app.models.user import User
from config.core.settings import get_settings

settings = get_settings()

class Token(Base):
    class Meta:
        table = to_table_name("Token")

    # Relationships
    user = fields.ForeignKeyField('models.User', related_name='tokens')

    # Token fields
    token = fields.CharField(max_length=8192, unique=True, index=True, null=False)
    expires_at = fields.DatetimeField(null=False)
    ip_address = fields.CharField(max_length=63, null=True)  # IPv6 max length
    user_agent = fields.TextField(max_length=1023, null=True)
    location = fields.JSONField(null=True)
    device = fields.JSONField(null=True)

    def valid(self) -> bool:
        return self.expires_at > DateTime.utc()

    async def cache_token(self, expires_minutes: int = settings.fetch("TOKEN_EXPIRATION_MINUTES")) -> bool:
        return await store_token(self.token, self.to_dict(), expires_minutes)
    
    async def delete_token(self) -> bool:
        return await delete_cached_token(self.token)

    async def refresh_token(self, expires_minutes: int = settings.fetch("TOKEN_EXPIRATION_MINUTES")) -> bool:
        return await refresh_cached_token(self.token, expires_minutes)
