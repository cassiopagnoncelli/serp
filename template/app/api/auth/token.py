import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
import logging

from app.utils.authentication import login_user, authenticate_user, find_user_by_email
from config.core.database import SessionDep
from lib.core.geo import get_device_info, get_location_info

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

router = APIRouter(tags = ["Authentication"])

@router.post(
    "/token",
    name="Login for Access Token",
    description="Authenticates a user and returns an access token"
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: SessionDep = None,
    request: Request = None,
    verbose: bool = False
) -> str:
    if verbose: 
        logger.debug(f"Login attempt for email: {form_data.username}")
        
    # Debug request headers
    if verbose:
        logger.debug("Request headers:")
        for key, value in request.headers.items():
            logger.debug(f"{key}: {value}")

    # Check if user exists
    user = find_user_by_email(form_data.username, session)
    if not user:
        if verbose:
            logger.warning(f"User not found for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if verbose:
        logger.debug(f"Found user: {user.email}")
    
    # Get device and location information
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    
    device_info = get_device_info(user_agent)
    location_info = get_location_info(ip_address)
    
    if verbose:
        logger.debug(f"Device info: {device_info}")
        logger.debug(f"Location info: {location_info}")
    
    # Try authentication
    token = login_user(
        email=form_data.username,
        password=form_data.password,
        ip_address=ip_address,
        user_agent=user_agent,
        device_info=device_info,
        location_info=location_info,
        session=session
    )
    
    if not token:
        if verbose:
            logger.warning(f"Authentication failed for email: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if verbose:
        logger.debug("Authentication successful")
    return token
