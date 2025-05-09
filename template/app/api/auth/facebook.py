from fastapi import HTTPException, APIRouter, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import RedirectResponse
import jwt
from requests import post, get
from os import getenv
from urllib.parse import urlencode
from sqlmodel import Session

from config.core.feature_flags import get_feature_flags
from app.models import User, UserStatus, LoginProvider
from lib.core.geo import get_device_info, get_location_info
from app.utils.authentication import *
from config.core.database import SessionDep

router = APIRouter(tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

feature_flags = get_feature_flags()

FACEBOOK_CLIENT_ID = "1040999621285256"
FACEBOOK_CLIENT_SECRET = "8350a0d68c694de5f50165923ef8e046"
FACEBOOK_REDIRECT_URI = "http://localhost:8000/auth/facebook/callback"

"""
Proceed to Facebook Developers Console at
https://developers.facebook.com/apps/
"""

@router.get(
  "/auth/facebook/login",
  name="Login with Facebook",
  description="Redirects to Facebook's OAuth2.0 login page"
)
async def login_facebook():
    query_params = {
        "client_id": FACEBOOK_CLIENT_ID,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "scope": "email,public_profile",
        "response_type": "code",
        "state": "facebook_login"  # Optional but recommended for security
    }
    redirect_uri = f"https://www.facebook.com/v18.0/dialog/oauth?{urlencode(query_params)}"
    return RedirectResponse(redirect_uri)

@router.get(
  "/auth/facebook/callback",
  name="Callback from Facebook Login",
  description="Handles the callback from Facebook's OAuth2.0 login page",
  include_in_schema=False
)
async def facebook_callback(
  code: str,
  session: SessionDep,
  request: Request = None
):
    # Exchange code for access token
    token_url = "https://graph.facebook.com/v18.0/oauth/access_token"
    data = {
        "client_id": FACEBOOK_CLIENT_ID,
        "client_secret": FACEBOOK_CLIENT_SECRET,
        "redirect_uri": FACEBOOK_REDIRECT_URI,
        "code": code
    }
    response = post(token_url, data=data)
    
    if not response.ok:
        raise HTTPException(status_code=401, detail="Failed to get Facebook access token")
    
    access_token = response.json().get("access_token")
    
    # Get user info from Facebook Graph API
    user_req = get(
        "https://graph.facebook.com/me",
        params={
            "fields": "id,email,name",
            "access_token": access_token
        }
    )

    if not user_req.ok:
        raise HTTPException(status_code=401, detail="Failed to get Facebook user info")

    user_info = user_req.json()
    
    # Find or create user
    user = find_user_by_email(user_info.get("email"), session)
    if not user:
        if feature_flags.get("social_login.create_user_on_facebook_login"):
            user = User(
                email=user_info.get("email"),
                password=random_password(),
                name=user_info.get("name"),
                status=UserStatus.active,
                login_provider=LoginProvider.facebook
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        else:
            raise HTTPException(status_code=401, detail="User not found")
    
    # Check if user is active
    if user.status != UserStatus.active:
        raise HTTPException(status_code=401, detail="User is not active")

    # Get device and location information
    user_agent = request.headers.get("user-agent")
    ip_address = request.client.host if request.client else None
    device_info = get_device_info(user_agent)
    location_info = get_location_info(ip_address)

    # Generate token
    token = login_user_with_facebook(
        email=user.email,
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        ip_address=ip_address,
        user_agent=user_agent,
        device=device_info,
        location=location_info,
        session=session
    )

    return { "token": token }
