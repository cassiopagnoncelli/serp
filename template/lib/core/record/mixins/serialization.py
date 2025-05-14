from typing import Any, Dict # Forward reference for 'Base'

from lib.core.serializers.json import *
from lib.core.serializers.bytecode import *
from lib.core.serializers.xml import *
from lib.core.serializers.yaml import *
from lib.core.serializers.csv import *

class SerializationMixin:
    """
    Mixin for model serialization and deserialization methods.
    Assumes self.to_dict() and self._meta.fields_map are available.
    """

    def to_bytecode(self) -> bytes:
        """Convert model instance to bytecode."""
        return serialize_bytecode(self.to_dict()) # type: ignore

    def from_bytecode(self, bytecode: bytes) -> 'Any': # type: ignore # Should resolve to 'Base' in context
        """Convert bytecode to model instance."""
        data = deserialize_bytecode(bytecode)
        # self._meta.fields_map comes from tortoise.models.Model
        for field_name, field_obj in self._meta.fields_map.items(): # type: ignore
            if field_name in data:
                setattr(self, field_name, data[field_name])
        return self

    def to_json(self) -> str:
        """Convert model instance to JSON string."""
        return serialize_json(self.to_dict()) # type: ignore
    
    def from_json(self, json_str: str) -> 'Any': # type: ignore
        """Convert JSON string to model instance."""
        attributes = deserialize_json(json_str)
        for field_name, field_obj in self._meta.fields_map.items(): # type: ignore
            if field_name in attributes:
                setattr(self, field_name, attributes[field_name])
        return self

    def to_yaml(self) -> str:
        """Convert model instance to YAML string."""
        return serialize_yaml(self.to_dict()) # type: ignore

    def from_yaml(self, yaml_str: str) -> 'Any': # type: ignore
        """Convert YAML string to model instance."""
        data = deserialize_yaml(yaml_str)
        # YAML might return a nested structure, get the first level data
        if isinstance(data, dict) and len(data) == 1:
            data = next(iter(data.values()))
        
        for field_name, field_obj in self._meta.fields_map.items(): # type: ignore
            if field_name in data:
                setattr(self, field_name, data[field_name])
        return self
    
    def to_csv(self) -> str:
        """Convert model instance to CSV string."""
        return serialize_csv(self.to_dict()) # type: ignore
    
    def from_csv(self, csv_str: str) -> 'Any': # type: ignore
        """Convert CSV string to model instance."""
        data = deserialize_csv(csv_str)
        for field_name, field_obj in self._meta.fields_map.items(): # type: ignore
            if field_name in data:
                setattr(self, field_name, data[field_name])
        return self

    def to_xml(self) -> str:
        """Convert model instance to XML string."""
        return serialize_xml(self.to_dict()) # type: ignore

    def from_xml(self, xml_str: str) -> 'Any': # type: ignore
        """Convert XML string to model instance."""
        attributes = deserialize_xml(xml_str)
        # Get the first (and only) key from the root dictionary
        root_key = next(iter(attributes))
        data = attributes[root_key]
        
        for field_name, field_obj in self._meta.fields_map.items(): # type: ignore
            if field_name in data:
                setattr(self, field_name, data[field_name])
        return self 