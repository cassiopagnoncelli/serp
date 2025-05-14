from tortoise import fields, models
from datetime import datetime, UTC
from typing import Any, Dict, ClassVar, Type, List
from pydantic import BaseModel, ConfigDict
from enum import Enum

from lib.core.dt import *
from lib.core.serializers.json import *
from lib.core.serializers.bytecode import *
from lib.core.serializers.xml import *
from lib.core.serializers.yaml import *
from lib.core.serializers.csv import *

def format_value(value: Any) -> str:
    """Format a value for string representation."""
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, Enum):
        return value.value
    elif value is None:
        return 'nil'
    return repr(value)

class Base(models.Model):
    # Common fields
    id = fields.IntField(pk=True)
    created_at = fields.DatetimeField()
    updated_at = fields.DatetimeField()

    # Default handlers for field transformations
    defaults = {}

    class Meta:
        abstract = True
        default_connection = "default"

    def __init__(self, *args, **kwargs):
        """Initialize model with field transformations."""
        # Apply default transformations
        for field, transform in self.defaults.items():
            if transform(kwargs):
                kwargs[field] = transform(kwargs)
        super().__init__(*args, **kwargs)

    def __setattr__(self, name, value):
        """Override setattr to handle field transformations."""
        # Check if this field has a transformation
        for field, transform in self.defaults.items():
            if name in transform.__code__.co_varnames:
                setattr(self, field, transform({name: value}))
                return
        super().__setattr__(name, value)

    @classmethod
    def pretty_print_format(cls) -> str:
        """Return the header for pretty printing."""
        return cls.__name__.upper()

    @classmethod
    async def delete_all(cls) -> bool:
        """Delete all records of this model."""
        await cls.all().delete()
        return True

    @classmethod
    async def head(cls, n: int = 1) -> 'Base | None':
        """Return the first record."""
        return await cls.all().order_by('id').limit(n)

    @classmethod
    async def tail(cls, n: int = 1, decreasing: bool = True) -> 'Base | None':
        """Return the last record."""
        result = await cls.all().order_by('-id').limit(n)
        return result if decreasing else result[::-1]
    
    # Alias for filter
    where = filter

    def __str__(self) -> str:
        """Return a string representation of the model with all its attributes."""
        attrs = []
        for field_name, field_obj in self._meta.fields_map.items():
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                attrs.append(f"{field_name}={format_value(value)}")
        return f"<{self.__class__.__name__} {', '.join(attrs)}>"
    
    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary for pretty printing."""
        result = {}
        # Get all fields from the model's meta
        for field_name, field_obj in self._meta.fields_map.items():
            # Always include the field, even if it's None
            value = getattr(self, field_name, None)
            result[field_name] = value
        return result
    # Aliases
    to_hash = to_dict

    def to_bytecode(self) -> bytes:
        """Convert model instance to bytecode."""
        return serialize_bytecode(self.to_dict())

    def from_bytecode(self, bytecode: bytes) -> 'Base':
        """Convert bytecode to model instance."""
        data = deserialize_bytecode(bytecode)
        # Set attributes on the instance
        for field_name, field_obj in self._meta.fields_map.items():
            if field_name in data:
                setattr(self, field_name, data[field_name])
        return self

    def to_json(self) -> str:
        """Convert model instance to JSON string."""
        return serialize_json(self.to_dict())
    
    def from_json(self, json_str: str) -> 'Base':
        """Convert JSON string to model instance."""
        attributes = deserialize_json(json_str)
        for field_name, field_obj in self._meta.fields_map.items():
            if field_name in attributes:
                setattr(self, field_name, attributes[field_name])
        return self

    def to_yaml(self) -> str:
        """Convert model instance to YAML string."""
        return serialize_yaml(self.to_dict())

    def from_yaml(self, yaml_str: str) -> 'Base':
        """Convert YAML string to model instance."""
        data = deserialize_yaml(yaml_str)
        # YAML might return a nested structure, get the first level data
        if isinstance(data, dict) and len(data) == 1:
            data = next(iter(data.values()))
        # Set attributes on the instance
        for field_name, field_obj in self._meta.fields_map.items():
            if field_name in data:
                setattr(self, field_name, data[field_name])
        return self
    
    def to_csv(self) -> str:
        """Convert model instance to CSV string."""
        return serialize_csv(self.to_dict())
    
    def from_csv(self, csv_str: str) -> 'Base':
        """Convert CSV string to model instance."""
        data = deserialize_csv(csv_str)
        # Set attributes on the instance
        for field_name, field_obj in self._meta.fields_map.items():
            if field_name in data:
                setattr(self, field_name, data[field_name])
        return self

    def to_xml(self) -> str:
        """Convert model instance to XML string."""
        return serialize_xml(self.to_dict())

    def from_xml(self, xml_str: str) -> 'Base':
        """Convert XML string to model instance."""
        attributes = deserialize_xml(xml_str)
        # Get the first (and only) key from the root dictionary
        root_key = next(iter(attributes))
        data = attributes[root_key]
        
        # Set attributes on the instance
        for field_name, field_obj in self._meta.fields_map.items():
            if field_name in data:
                setattr(self, field_name, data[field_name])
        return self

    async def get_all_attributes(self) -> Dict[str, Any]:
        """Get all model fields and their values as a dictionary."""
        return await self.to_dict()

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
        await super().update(**kwargs)

    async def reload(self) -> 'Base | None':
        """Reload the instance from the database.
        
        Returns:
            Base | None: The reloaded instance if it exists in the database, None otherwise.
        """
        if not self.id:
            return None
        try:
            # Fetch fresh data from database
            fresh_instance = await self.__class__.get(id=self.id)
            # Update all attributes of current instance
            for field_name in self._meta.fields_map:
                setattr(self, field_name, getattr(fresh_instance, field_name))
            return self
        except Exception:
            # If record doesn't exist or any other error occurs, return None
            return None

    def format(self, to_model: Type[BaseModel]) -> BaseModel:
        """Convert the model instance to a Pydantic model."""
        return to_model(**self.to_dict())

# Base Pydantic model with common fields
class BasePydanticModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
