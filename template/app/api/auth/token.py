import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import logging

from app.utils.authentication import login_user_with_password, authenticate_user, find_user_by_email
from lib.core.geo import get_device_info, get_location_info
from config.core.settings import get_settings

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

router = APIRouter(tags = ["Authentication"])

@router.post(
    "/auth/token",
    name="Login for Access Token",
    description="Authenticates a user and returns an access token"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None
) -> str:
    # Check if user exists
    user = await find_user_by_email(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
  
    # Get device and location information
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    device_info = get_device_info(user_agent)
    location_info = get_location_info(ip_address)

    # Try authentication
    token = await login_user_with_password(
        email=form_data.username,
        password=form_data.password,
        ip_address=ip_address,
        user_agent=user_agent,
        device=device_info,
        location=location_info
    )
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
