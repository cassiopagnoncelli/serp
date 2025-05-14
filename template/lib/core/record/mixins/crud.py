from tortoise import fields, models
from datetime import datetime, UTC
from typing import Any, Dict, ClassVar, Type, List, TypeVar
from pydantic import BaseModel, ConfigDict
from enum import Enum
import asyncio

from lib.core.dt import *

T = TypeVar('T', bound='CRUDMixin')

class CRUDMixin:
    """
    Mixin for common CRUD operations.
    Assumes self is a Tortoise ORM model.
    """

    @classmethod
    async def delete_all(cls: Type[T]) -> bool:
        """Delete all records of this model."""
        await cls.all().delete()  # type: ignore
        return True
    
    async def save(self, *args, **kwargs):
        """Save the model instance with field transformations."""
        # Apply transformations to instance attributes
        for field, transform in self.defaults.items():
            # Get all variables needed by the transform function
            needed_vars = transform.__code__.co_varnames
            transform_kwargs = {var: getattr(self, var) for var in needed_vars if hasattr(self, var)}
            if transform_kwargs:
                setattr(self, field, transform(transform_kwargs))
                # Clean up source attributes if they exist
                for var in needed_vars:
                    if hasattr(self, var):
                        delattr(self, var)

        # Set timestamps if this is a new record
        if not self.id:
            current_timestamp = DateTime.utc()
            self.created_at = current_timestamp.replace(tzinfo=None)
            self.updated_at = current_timestamp.replace(tzinfo=None)
        else:
            # Update the updated_at field before saving
            self.updated_at = DateTime.utc().replace(tzinfo=None)
        
        # Ensure all datetime fields are timezone-naive
        for field_name, field_obj in self._meta.fields_map.items():
            if isinstance(field_obj, fields.DatetimeField):
                value = getattr(self, field_name)
                if value and value.tzinfo is not None:
                    setattr(self, field_name, value.replace(tzinfo=None))
        
        # Use direct update API if we have a primary key
        if hasattr(self, 'pk') and self.pk:
            # Prepare update data
            update_data = {}
            for field_name, field_obj in self._meta.fields_map.items():
                if field_name != 'id' and field_name not in ('created_at', 'updated_at'):
                    value = getattr(self, field_name)
                    update_data[field_name] = value
            
            # Add updated_at to update data
            update_data['updated_at'] = self.updated_at
            
            # Execute the update and refresh the instance
            await self.__class__.filter(id=self.pk).update(**update_data)
            refreshed = await self.__class__.get(id=self.pk)
            
            # Copy updated attributes back to this instance
            for field_name in self._meta.fields_map:
                if field_name != 'id':  # Don't update id
                    setattr(self, field_name, getattr(refreshed, field_name))
            
            return self
        else:
            return await super().save(*args, **kwargs)

    async def update(self, **kwargs):
        """Handle field transformations during updates."""
        # Apply default transformations
        for field, transform in self.defaults.items():
            if transform(kwargs):
                kwargs[field] = transform(kwargs)
        
        # Update the instance using Tortoise's filter().update()
        await self.__class__.filter(id=self.pk).update(**kwargs)
        
        # Refresh the instance with updated values
        refreshed = await self.__class__.get(id=self.pk)
        
        # Only update fields that are not properties
        for field_name in self._meta.fields_map:
            if field_name != 'id':  # Don't update id
                try:
                    # Try to set the attribute directly
                    setattr(self, field_name, getattr(refreshed, field_name))
                except AttributeError:
                    # Skip if it's a property without a setter
                    continue
        
        return self

