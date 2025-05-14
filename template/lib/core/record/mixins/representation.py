from typing import Any, Dict, Type
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

def format_value(value: Any) -> str:
    """Format a value for string representation."""
    if isinstance(value, datetime):
        return value.isoformat()
    elif isinstance(value, Enum):
        return value.value
    elif value is None:
        return 'nil'
    return repr(value)

class RepresentationMixin:
    """
    Mixin for model representation methods like __str__, to_dict, etc.
    """

    @classmethod
    def pretty_print_format(cls) -> str:
        """Return the header for pretty printing."""
        return cls.__name__.upper()

    def __str__(self) -> str:
        """Return a string representation of the model with all its attributes."""
        attrs = []
        # self._meta.fields_map comes from tortoise.models.Model
        for field_name, field_obj in self._meta.fields_map.items(): # type: ignore
            if hasattr(self, field_name):
                value = getattr(self, field_name)
                attrs.append(f"{field_name}={format_value(value)}")
        return f"<{self.__class__.__name__} {', '.join(attrs)}>"
    
    def __repr__(self) -> str:
        return self.__str__()

    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        result = {}
        # self._meta.fields_map comes from tortoise.models.Model
        for field_name, field_obj in self._meta.fields_map.items(): # type: ignore
            value = getattr(self, field_name, None)
            result[field_name] = value
        return result
    
    # Alias
    to_hash = to_dict

    async def get_all_attributes(self) -> Dict[str, Any]:
        """Get all model fields and their values as a dictionary."""
        # This was originally await self.to_dict(), but to_dict is synchronous.
        # Returning self.to_dict() directly. If to_dict ever becomes async, this remains correct.
        return self.to_dict()

    def format(self, to_model: Type[BaseModel]) -> BaseModel:
        """Convert the model instance to a Pydantic model."""
        return to_model(**self.to_dict()) 