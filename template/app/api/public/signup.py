import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, SecretStr

from app.schemas.user import UserCreate, UserPublic
from app.utils.authentication import find_user_by_email
from config.core.database import SessionDep
from lib.core.authentication.passwords import encrypt_password
from app.models import User

router = APIRouter(tags = ["Sign Up"])

@router.post(
    "/public/signup",
    name="Sign up",
    description="Signs up a user",
    response_model=UserPublic
)
async def signup(
    email: EmailStr,
    password: SecretStr,
    confirm_password: SecretStr,
    name: str,
    account_uuid: Optional[str] = None,
    session: SessionDep = None
) -> UserPublic:
    # Check if user exists
    user = find_user_by_email(email, session)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    # Check if password and confirm password match
    if password.get_secret_value() != confirm_password.get_secret_value():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    # Create user
    encrypted_password = encrypt_password(password.get_secret_value())
    user_data = UserCreate(
        email=email,
        enc_password=encrypted_password,
        name=name,
        account_uuid=account_uuid
    )
    
    # Create actual User model instance
    user = User(**user_data.model_dump())
    session.add(user)
    session.commit()
    session.refresh(user)

    return UserPublic(
        uuid=user.uuid,
        name=user.name,
        email=user.email
    )
