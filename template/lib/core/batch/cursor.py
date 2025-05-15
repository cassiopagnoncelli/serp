from typing import AsyncGenerator, TypeVar, Optional, Any
from tortoise.models import Model
from tortoise.queryset import QuerySet

T = TypeVar('T', bound=Model)

# Example usage.
#
#   async def print_user_ids():
#       count = 0
#       async for user in CursorBatchProcessor.find_each(
#           User.filter(id__gt=0),
#           batch_size=10
#       ):
#           print(user.id)
#           count += 1  
#           if count % 10 == 0:
#               print(f"Processed {count} users...")
#       print(f"Total processed: {count} inactive users")
#
#
class CursorBatchProcessor:
    """
    Batch processor using cursor-based pagination for efficient iteration
    """
    @staticmethod
    async def find_each(
        queryset: QuerySet[T],
        batch_size: int = 1000,
        cursor_field: str = 'id',
        start_value: Optional[Any] = None,
        finish_value: Optional[Any] = None
    ) -> AsyncGenerator[T, None]:
        """
        Process records one by one using cursor-based pagination
        
        Args:
            queryset: The Tortoise ORM queryset to process
            batch_size: Number of records per batch (default: 1000)
            cursor_field: Field to use as cursor (default: 'id')
            start_value: Starting value for cursor (optional)
            finish_value: Ending value for cursor (optional)
        
        Yields:
            Individual model instances
        """
        current_queryset = queryset.order_by(cursor_field)
        cursor_value = start_value
        
        # Apply finish filter if provided
        if finish_value is not None:
            current_queryset = current_queryset.filter(**{f"{cursor_field}__lte": finish_value})
        
        while True:
            if cursor_value is not None:
                current_queryset = current_queryset.filter(
                    **{f"{cursor_field}__gt": cursor_value}
                )
            
            batch = await current_queryset.limit(batch_size)
            
            if not batch:
                break
            
            for record in batch:
                yield record
                cursor_value = getattr(record, cursor_field)
