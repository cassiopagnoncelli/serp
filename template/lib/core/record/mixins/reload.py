from tortoise import fields, models
from datetime import datetime, UTC
from typing import Any, Dict, ClassVar, Type, List, TypeVar
from pydantic import BaseModel, ConfigDict
from enum import Enum
import asyncio

from lib.core.dt import *

T = TypeVar('T', bound='ReloadMixin')

class ReloadMixin:
    """
    Mixin for common reload operations.
    Assumes self is a Tortoise ORM model.
    """
    async def reload(self) -> Any:  # type: ignore # Returns Base | None in context
        """Reload the instance from the database.
        
        Returns:
            Base | None: The reloaded instance if it exists in the database, None otherwise.
        """
        if not hasattr(self, 'id') or not self.id:  # if not self.id:
            return None
        try:
            # Fetch fresh data from database
            fresh_instance = await self.__class__.get(id=self.id)  # type: ignore
            # Update all attributes of current instance
            for field_name in self._meta.fields_map:  # type: ignore
                setattr(self, field_name, getattr(fresh_instance, field_name))
            return self
        except Exception:
            # If record doesn't exist or any other error occurs, return None
            return None
