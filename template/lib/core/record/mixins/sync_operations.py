import asyncio
from typing import Any, List, ClassVar, Type, TypeVar

T = TypeVar('T', bound='SyncOperationsMixin')

class SyncOperationsMixin:
    """
    Mixin for synchronous operation wrappers.
    Assumes self is a Tortoise ORM model with async operations.
    """
    # Class-level event loop for sync operations
    _loop: ClassVar[asyncio.AbstractEventLoop] = None

    @classmethod
    def _get_loop(cls) -> asyncio.AbstractEventLoop:
        """Get or create the event loop for sync operations."""
        if cls._loop is None or cls._loop.is_closed():
            cls._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(cls._loop)
        return cls._loop

    # Existing operations.
    @classmethod
    def _all(cls: Type[T]) -> Any:  # type: ignore # Returns Base | None in context
        """Return all records."""
        loop = cls._get_loop()
        return loop.run_until_complete(cls.all())  # type: ignore
    aall = _all
    sall = _all

    # Query Helpers.
    @classmethod
    def _first(cls: Type[T], n: int = 1) -> Any:  # type: ignore # Returns Base | None in context
        """Return the first record synchronously."""
        loop = cls._get_loop()
        return loop.run_until_complete(cls.head(n))  # type: ignore
    afirst = _first
    sfirst = _first

    @classmethod
    def _last(cls: Type[T], n: int = 1) -> Any:  # type: ignore # Returns Base | None in context
        """Return the last record synchronously."""
        loop = cls._get_loop()
        return loop.run_until_complete(cls.last(n))  # type: ignore
    alast = _last
    slast = _last

    @classmethod
    def _head(cls: Type[T], n: int = 1) -> List[Any]:  # type: ignore # Returns List[Base] in context
        """Return the first record synchronously."""
        loop = cls._get_loop()
        return loop.run_until_complete(cls.head(n))  # type: ignore
    ahead = _head
    shead = _head

    @classmethod
    def _tail(cls: Type[T], n: int = 1, decreasing: bool = True) -> List[Any]:  # type: ignore # Returns List[Base] in context
        """Return the last record synchronously."""
        loop = cls._get_loop()
        return loop.run_until_complete(cls.tail(n, decreasing))  # type: ignore
    atail = _tail
    stail = _tail

    # CRUD Operations.
    @classmethod
    def _create(cls: Type[T], **kwargs) -> Any:  # type: ignore # Returns Base in context
        """Create a new instance synchronously."""
        loop = cls._get_loop()
        return loop.run_until_complete(cls.create(**kwargs))  # type: ignore
    acreate = _create
    screate = _create

    def _update(self, **kwargs) -> Any:  # type: ignore # Returns Base in context
        """Update the instance synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(self.update(**kwargs))  # type: ignore
    aupdate = _update
    supdate = _update

    def _delete(self) -> bool:
        """Delete the instance synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(self.delete())  # type: ignore
    adelete = _delete
    sdelete = _delete

    def _save(self, *args, **kwargs) -> Any:  # type: ignore # Returns Base in context
        """Save the instance synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(self.save(*args, **kwargs))  # type: ignore
    asave = _save
    ssave = _save

    # Reload Operations.
    def _reload(self) -> Any:  # type: ignore # Returns Base | None in context
        """Reload the instance synchronously."""
        loop = self._get_loop()
        return loop.run_until_complete(self.reload())  # type: ignore
    areload = _reload
    sreload = _reload

    # Find Operations.
    @classmethod
    def _find(cls: Type[T], id: Any) -> Any:  # type: ignore # Returns Base | None in context
        """Find the instance synchronously."""
        loop = cls._get_loop()
        return loop.run_until_complete(cls.find(id))  # type: ignore
    afind = _find
    sfind = _find

    @classmethod
    def _find_by(cls, **kwargs: Any) -> Any:  # type: ignore # Returns Base | None in context
        """Find the instance synchronously."""
        loop = cls._get_loop()
        return loop.run_until_complete(cls.find_by(**kwargs))  # type: ignore
    afind_by = _find_by
    sfind_by = _find_by
