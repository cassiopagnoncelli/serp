from typing import Any, List, TypeVar, Type

T = TypeVar('T', bound='QueryHelpersMixin')

class QueryHelpersMixin:
    """
    Mixin for common query helper methods.
    Assumes self is a Tortoise ORM model.
    """
    @classmethod
    async def last(cls: Type[T], n: int = 1) -> Any:  # type: ignore # Returns Base | None in context
        """Return the last record."""
        results = await cls.all().order_by('-id').limit(n)  # type: ignore
        return results[0] if len(results) > 0 else None

    @classmethod
    async def head(cls: Type[T], n: int = 1) -> List[Any]:  # type: ignore # Returns List[Base] in context
        """Return the first n records."""
        return await cls.all().order_by('id').limit(n)  # type: ignore

    @classmethod
    async def tail(cls: Type[T], n: int = 1, decreasing: bool = True) -> List[Any]:  # type: ignore # Returns List[Base] in context
        """Return the last n records."""
        result = await cls.all().order_by('-id').limit(n)  # type: ignore
        return result if decreasing else result[::-1]

    async def reload(self) -> Any:  # type: ignore # Returns Base | None in context
        """Reload the instance from the database.
        
        Returns:
            Base | None: The reloaded instance if it exists in the database, None otherwise.
        """
        if not hasattr(self, 'id') or not self.id:
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

    # Alias for filter
    where = filter