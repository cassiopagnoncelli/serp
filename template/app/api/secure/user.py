from fastapi import APIRouter, Depends

from app.schemas.user import *
from app.utils.authentication import get_current_user

router = APIRouter(tags=["Users API"])

@router.get(
    "/secure/me",
    response_model=UserPublic
)
async def read_user(user: UserTokenizable = Depends(get_current_user)) -> UserPublic:
    return UserPublic(**user.dict())
