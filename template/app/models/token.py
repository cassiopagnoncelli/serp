from tortoise import fields
from datetime import datetime, timezone
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict

from lib.core.record.inflection import to_table_name
from lib.core.record.base import Base
from lib.core.dt import DateTime
from app.utils.auth_tokens import store_token, get_cached_token, delete_cached_token, refresh_cached_token
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

    @classmethod
    async def check_token(cls, token: str) -> bool:
        if settings.fetch("CACHE_TOKENS") == "true":
            tokstr = await get_cached_token(token)
            return (tokstr is not None and len(tokstr) > 0)
        else:
            obj = await cls.filter(token=token).first()
            return (obj is not None and len(obj.token) > 0)

    def valid(self) -> bool:
        utc_now = DateTime.utc().replace(tzinfo=timezone.utc)
        return self.expires_at > utc_now

    async def cache_token(self, expires_minutes: int = settings.fetch("ACCESS_TOKEN_EXPIRE_MINUTES")) -> bool:
        return await store_token(self.token, self.to_dict(), expires_minutes)

    async def delete_token(self) -> bool:
        return await delete_cached_token(self.token)

    async def refresh_token(self, expires_minutes: int = settings.fetch("ACCESS_TOKEN_EXPIRE_MINUTES")) -> bool:
        return await refresh_cached_token(self.token, expires_minutes)

    async def destroy(self) -> None:
        await self.delete_token()
        await self.delete()
