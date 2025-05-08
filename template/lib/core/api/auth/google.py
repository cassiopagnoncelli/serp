# from fastapi import Depends, HTTPException, APIRouter
# from fastapi.security import OAuth2PasswordBearer
# from fastapi.responses import RedirectResponse
# from jwt import decode
# from requests import post, get
# from os import getenv
# from urllib.parse import urlencode

# router = APIRouter(tags=["Authentication"])
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

# """
# Proceed to OAuth2.0 Credentials at
# https://console.cloud.google.com/apis/credentials
# """

# @router.get(
#   "/auth/google/login",
#   name="Login with Google",
#   description="Redirects to Google's OAuth2.0 login page"
# )
# async def login_google():
#     query_params = {
#         "response_type": "code",
#         "client_id": getenv("GOOGLE_CLIENT_ID"),
#         "redirect_uri": getenv("GOOGLE_REDIRECT_URI"),
#         "scope": "openid profile email",
#         "access_type": "offline",
#     }
#     redirect_uri = f"https://accounts.google.com/o/oauth2/auth?{urlencode(query_params)}"
#     return RedirectResponse(redirect_uri)

# @router.get(
#   "/auth/google/callback",
#   name="Callback from Google Login",
#   description="Handles the callback from Google's OAuth2.0 login page"
# )
# async def google_callback(code: str):
#     token_url = "https://accounts.google.com/o/oauth2/token"
#     data = {
#         "code": code,
#         "client_id": getenv("GOOGLE_CLIENT_ID"),
#         "client_secret": getenv("GOOGLE_CLIENT_SECRET"),
#         "redirect_uri": getenv("GOOGLE_REDIRECT_URI"),
#         "grant_type": "authorization_code",
#     }
#     response = post(token_url, data=data)
#     access_token = response.json().get("access_token")
#     id_token = response.json().get("id_token")
    
#     # Store the id_token for later use
#     # In a real application, you would store this in a database
    
#     user_info = get(
#         "https://www.googleapis.com/oauth2/v1/userinfo", 
#         headers={"Authorization": f"Bearer {access_token}"}
#     )
#     return user_info.json()

# @router.get("/auth/google/token")
# async def get_token(token: str = Depends(oauth2_scheme)):
#     return decode(token, getenv("GOOGLE_CLIENT_SECRET"), algorithms=["HS256"])
