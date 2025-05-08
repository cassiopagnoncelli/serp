from fastapi import APIRouter, HTTPException, Query, Depends, Security
from sqlmodel import Session, SQLModel, select, update
from typing import Annotated
from fastapi.security import OAuth2PasswordBearer, SecurityScopes, HTTPBearer, HTTPAuthorizationCredentials
from app.models.user import *
from app.schemas.user import *
from config.core.database import *
from app.utils.authentication import decode_user_token, find_user_by_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_scheme = HTTPBearer()

router = APIRouter(tags=["Users API"])

def get_current_user(
    oauth_token: str = Depends(oauth2_scheme),
    bearer_token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UserTokenizable:
    # Try OAuth2 token first
    token_data = decode_user_token(oauth_token)
    if not token_data:
        # Try bearer token
        token_data = decode_user_token(bearer_token.credentials)
        if not token_data:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    return token_data

@router.get(
    "/secure/me",
    response_model=UserPublic
)
def read_user(user: UserTokenizable = Depends(get_current_user)) -> UserPublic:
    return user
