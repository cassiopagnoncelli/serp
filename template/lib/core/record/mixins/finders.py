from tortoise import fields, models
from datetime import datetime, UTC
from typing import Any, Dict, ClassVar, Type, List, TypeVar
from pydantic import BaseModel, ConfigDict
from enum import Enum
import asyncio
from tortoise.exceptions import DoesNotExist

from lib.core.dt import *

T = TypeVar('T', bound='FindersMixin')

class FindersMixin:
    """
    Mixin for common find operations.
    Assumes self is a Tortoise ORM model.
    """
    @classmethod
    async def find(cls, id: Any) -> Any:  # type: ignore # Returns Base | None in context
        """Find the instance from the database.
        
        Args:
            id: The ID to search for
        
        Returns:
            First instance found, or None if not found.
        """
        try:
            return await cls.get(id=id)
        except DoesNotExist:
            return None

    @classmethod
    async def find_by(cls, **kwargs: Any) -> Any:  # type: ignore # Returns Base | None in context
        """Find the instance from the database by the given kwargs.
        
        Args:
            **kwargs: The filter criteria to search by
            
        Returns:
            First instance found, or None if not found.
        """
        try:
            return await cls.get(**kwargs)
        except DoesNotExist:
            return None
