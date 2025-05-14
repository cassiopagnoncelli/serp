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

    # Alias for filter
    where = filter