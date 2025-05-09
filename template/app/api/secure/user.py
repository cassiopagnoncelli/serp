from fastapi import APIRouter, Depends

from app.schemas.user import *
from app.utils.authentication import get_current_user

router = APIRouter(tags=["Users API"])

@router.get(
    "/secure/me",
    response_model=UserPublic
)
def read_user(user: UserCreate = Depends(get_current_user)) -> UserPublic:
    return user
