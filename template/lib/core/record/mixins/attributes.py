from tortoise import fields
from typing import Any, Dict, ClassVar, Type, List, TypeVar
from enum import Enum
import asyncio

T = TypeVar('T', bound='AttributesMixin')

class AttributesMixin:
    """
    Mixin for common attribute operations.
    Assumes self is a Tortoise ORM model.
    """
    # Common fields
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField(timezone=False, null=False)
    updated_at = fields.DatetimeField(timezone=False, null=False)
