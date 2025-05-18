import asyncio
from typing import Any, Dict, List, Type, TypeVar, Optional, Union, Callable
from tortoise import Tortoise
from tortoise.models import Model
from tortoise.queryset import QuerySet

T = TypeVar('T', bound=Model)

class SyncTortoiseAdapter:
    """
    Synchronous adapter for Tortoise ORM models for use in the console.
    
    This adapter allows running Tortoise ORM operations synchronously,
    making it easier to use in the console environment.
    
    Usage:
        # In the console
        user = User.create(email='test@example.com', password='password')
        all_users = User.all()
        user_by_email = User.find_by(email='test@example.com')
    """
    
    def __init__(self):
        """Initialize with a new event loop for running async operations."""
        self.loop = asyncio.new_event_loop()
        self._models_cache = {}
    
    def _run_async(self, coro):
        """Run a coroutine in the event loop."""
        return self.loop.run_until_complete(coro)
    
    def get_model(self, model_name: str) -> Type[Any]:
        """
        Get a Tortoise model by its name and make it accessible synchronously.
        
        Args:
            model_name: The name of the model, e.g., 'models.User'
            
        Returns:
            A proxy class for the model with synchronous methods
        """
        if model_name in self._models_cache:
            return self._models_cache[model_name]
        
        # Get the actual model class
        model_class = Tortoise.apps.get('models').get(model_name.split('.')[-1])
        
        # Create a proxy class
        class ModelProxy:
            """Proxy class for Tortoise model with synchronous methods."""
            
            _model_class = model_class
            _adapter = self
            
            def __init__(self, **kwargs):
                """Initialize a new model instance."""
                self._instance = None
                self._kwargs = kwargs
                
                # Create the instance asynchronously and cache it
                if kwargs:
                    self._instance = self._adapter._run_async(self._model_class.create(**kwargs))
            
            def __getattr__(self, name):
                """Delegate attribute access to the underlying model instance."""
                if self._instance is None:
                    raise AttributeError(f"Instance not created yet for {name}")
                return getattr(self._instance, name)
            
            @classmethod
            def create(cls, **kwargs) -> Any:
                """Create a new model instance synchronously."""
                return cls._adapter._run_async(cls._model_class.create(**kwargs))
            
            @classmethod
            def all(cls) -> List[Any]:
                """Get all model instances synchronously."""
                return cls._adapter._run_async(cls._model_class.all())
            
            @classmethod
            def filter(cls, **kwargs) -> List[Any]:
                """Filter model instances synchronously."""
                return cls._adapter._run_async(cls._model_class.filter(**kwargs))
            
            @classmethod
            def where(cls, **kwargs) -> List[Any]:
                """Alias for filter."""
                return cls.filter(**kwargs)
            
            @classmethod
            def get(cls, **kwargs) -> Any:
                """Get a model instance synchronously."""
                return cls._adapter._run_async(cls._model_class.get(**kwargs))
            
            @classmethod
            def find(cls, id: Any) -> Any:
                """Find a model instance by ID synchronously."""
                return cls._adapter._run_async(cls._model_class.find(id))
            
            @classmethod
            def find_by(cls, **kwargs) -> Any:
                """Find a model instance by attributes synchronously."""
                return cls._adapter._run_async(cls._model_class.find_by(**kwargs))
            
            @classmethod
            def first(cls) -> Any:
                """Get the first model instance synchronously."""
                results = cls._adapter._run_async(cls._model_class.all().limit(1))
                return results[0] if results else None
            
            @classmethod
            def last(cls) -> Any:
                """Get the last model instance synchronously."""
                return cls._adapter._run_async(cls._model_class.last())
            
            @classmethod
            def head(cls, n: int = 1) -> List[Any]:
                """Get the first n model instances synchronously."""
                return cls._adapter._run_async(cls._model_class.head(n))
            
            @classmethod
            def tail(cls, n: int = 1, decreasing: bool = True) -> List[Any]:
                """Get the last n model instances synchronously."""
                return cls._adapter._run_async(cls._model_class.tail(n, decreasing))
            
            @classmethod
            def count(cls) -> int:
                """Count model instances synchronously."""
                return cls._adapter._run_async(cls._model_class.all().count())
            
            @classmethod
            def delete_all(cls) -> int:
                """Delete all model instances synchronously."""
                return cls._adapter._run_async(cls._model_class.delete_all())
            
            def save(self) -> Any:
                """Save the model instance synchronously."""
                if self._instance is None:
                    # Create a new instance
                    self._instance = self._adapter._run_async(self._model_class.create(**self._kwargs))
                    return self._instance
                else:
                    # Update existing instance
                    return self._adapter._run_async(self._instance.save())
            
            def update(self, **kwargs) -> Any:
                """Update the model instance synchronously."""
                if self._instance is None:
                    raise AttributeError("Instance not created yet")
                
                # Update instance attributes
                for key, value in kwargs.items():
                    setattr(self._instance, key, value)
                
                return self._adapter._run_async(self._instance.save())
            
            def delete(self) -> bool:
                """Delete the model instance synchronously."""
                if self._instance is None:
                    raise AttributeError("Instance not created yet")
                return self._adapter._run_async(self._instance.delete())
            
            def reload(self) -> Any:
                """Refresh the model instance from the database synchronously."""
                if self._instance is None:
                    raise AttributeError("Instance not created yet")
                return self._adapter._run_async(self._instance.reload())
            
            # Alias for reload
            refresh = reload
            
            def __repr__(self):
                """String representation of the model instance."""
                if self._instance is None:
                    return f"<Uninitialized {model_class.__name__}>"
                
                # Get the model's string representation or fall back to default
                try:
                    return self._instance.__repr__()
                except:
                    attrs = []
                    # Show id and a few key attributes if they exist
                    if hasattr(self._instance, 'id'):
                        attrs.append(f"id={self._instance.id}")
                    if hasattr(self._instance, 'uuid'):
                        attrs.append(f"uuid={self._instance.uuid}")
                    if hasattr(self._instance, 'email'):
                        attrs.append(f"email={self._instance.email}")
                    if hasattr(self._instance, 'name'):
                        attrs.append(f"name={self._instance.name}")
                    
                    return f"<{model_class.__name__} {' '.join(attrs)}>"
        
        # Cache and return the proxy class
        self._models_cache[model_name] = ModelProxy
        return ModelProxy
    
    def __getattr__(self, name):
        """
        Allow accessing models as attributes.
        
        For example:
        adapter.User instead of adapter.get_model('models.User')
        """
        try:
            return self.get_model(f"models.{name}")
        except:
            raise AttributeError(f"No such model: {name}")

# Helper function to make console usage easier
def get_tortoise_adapter():
    """Get a SyncTortoiseAdapter instance."""
    return SyncTortoiseAdapter()
