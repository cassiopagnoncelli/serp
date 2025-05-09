import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import logging

from app.models.user import UserCreate
from app.utils.authentication import find_user_by_email
from config.core.database import SessionDep

router = APIRouter(tags = ["Sign Up"])

@router.post(
    "/public/signup",
    name="Sign up",
    description="Signs up a user"
)
async def signup(
    email: EmailStr,
    password: str,
    confirm_password: str,
    name: str,
    session: SessionDep = None
) -> str:
    # Check if user exists
    user = find_user_by_email(email, session)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    # Check if password and confirm password match
    if password != confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    # Create user
    user = UserCreate(email=email, password=password, name=name)
    session.add(user)
    session.commit()
    session.refresh(user)

    return user
