from tortoise import fields
from datetime import datetime
from typing import Any, Dict
from pydantic import BaseModel, ConfigDict

from lib.core.record.inflection import to_table_name
from lib.core.record.base import Base

class Token(Base):
    class Meta:
        table = to_table_name("Token")

    # Relationships
    user_id = fields.IntField(index=True, null=False)

    # Token fields
    token = fields.CharField(max_length=1023, unique=True, index=True, null=False)
    expires_at = fields.DatetimeField(null=False)
    ip_address = fields.CharField(max_length=63, null=True)  # IPv6 max length
    user_agent = fields.TextField(max_length=1023, null=True)
    location = fields.JSONField(null=True)
    device = fields.JSONField(null=True)
