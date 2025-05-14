from tortoise import fields, models
from datetime import datetime, UTC
from typing import Any, Dict, ClassVar, Type, List
from pydantic import BaseModel, ConfigDict
from enum import Enum
import asyncio

from lib.core.record.mixins.representation import RepresentationMixin
from lib.core.record.mixins.serialization import SerializationMixin
from lib.core.record.mixins.query_helpers import QueryHelpersMixin
from lib.core.record.mixins.sync_operations import SyncOperationsMixin
from lib.core.record.mixins.crud import CRUDMixin
from lib.core.record.mixins.reload import ReloadMixin
from lib.core.record.mixins.attributes import AttributesMixin

class Base(
    RepresentationMixin,
    SerializationMixin,
    QueryHelpersMixin,
    SyncOperationsMixin,
    CRUDMixin,
    ReloadMixin,
    AttributesMixin,
    models.Model
):
    """
    Base model class with common fields and functionality.
    Inherits from mixins to provide comprehensive functionality while maintaining clean separation of concerns.
    """

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

# Base Pydantic model with common fields
class BasePydanticModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime
