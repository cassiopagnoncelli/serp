from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import RedirectResponse
from requests import post, get
from os import getenv
from urllib.parse import urlencode

from config.core.feature_flags import get_feature_flags
from app.models import User, UserStatus, LoginProvider
from lib.core.geo import get_device_info, get_location_info
from app.utils.authentication import *

router = APIRouter(tags=["Authentication"])

feature_flags = get_feature_flags()

"""
Proceed to OAuth2.0 Credentials at
https://console.cloud.google.com/apis/credentials
"""

@router.get(
  "/auth/google/login",
  name="Login with Google",
  description="Redirects to Google's OAuth2.0 login page"
)
async def login_google():
    query_params = {
        "response_type": "code",
        "client_id": getenv("GOOGLE_CLIENT_ID"),
        "redirect_uri": getenv("GOOGLE_REDIRECT_URI"),
        "scope": "openid profile email",
        "access_type": "offline",
    }
    redirect_uri = f"https://accounts.google.com/o/oauth2/auth?{urlencode(query_params)}"
    return RedirectResponse(redirect_uri)

@router.get(
  "/auth/google/callback",
  name="Callback from Google Login",
  description="Handles the callback from Google's OAuth2.0 login page",
  include_in_schema=False
)
async def google_callback(
  code: str,
  request: Request = None
):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": getenv("GOOGLE_CLIENT_ID"),
        "client_secret": getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": getenv("GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code"
    }
    response = post(token_url, data=data)
    access_token = response.json().get("access_token")
    id_token = response.json().get("id_token")
    user_req = get(
        "https://www.googleapis.com/oauth2/v1/userinfo", 
        headers={"Authorization": f"Bearer {access_token}"}
    )

    if not user_req.ok:
      raise HTTPException(status_code=401, detail="Google login failed")

    # We are not storing google login info in our database
    # instead we are merely using it to authenticate the user.
    user_info = user_req.json()

    # Find or create user
    user = await find_user_by_email(user_info.get("email"))
    if not user:
      if feature_flags.get("social_login.create_user_on_google_login"):
        user = await User.create(
            email=user_info.get("email"),
            password=random_password(),
            name=user_info.get("name"),
            status=UserStatus.active,
            login_provider=LoginProvider.google
        )
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
    token = await login_user_with_google(
        email=user.email,
        expires_minutes=ACCESS_TOKEN_EXPIRE_MINUTES,
        ip_address=ip_address,
        user_agent=user_agent,
        device=device_info,
        location=location_info
    )

    return { "token": token }
