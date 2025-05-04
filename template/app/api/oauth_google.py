from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordBearer
from jwt import decode
from requests import post, get
from os import getenv

router = APIRouter(tags=["Google Login"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "token")

@router.get("/login/google")
async def login_google():
    return {
        "url": f"https://accounts.google.com/o/oauth2/auth?response_type=code&client_id={getenv("GOOGLE_CLIENT_ID")}&redirect_uri={getenv("GOOGLE_REDIRECT_URI")}&scope=openid%20profile%20email&access_type=offline"
    }

@router.get("/oauth2/google")
async def auth_google(code: str):
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": getenv("GOOGLE_CLIENT_ID"),
        "client_secret": getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uri": getenv("GOOGLE_REDIRECT_URI"),
        "grant_type": "authorization_code",
    }
    response = post(token_url, data=data)
    access_token = response.json().get("access_token")
    id_token = response.json().get("id_token")
    
    # Store the id_token for later use
    # In a real application, you would store this in a database
    
    user_info = get(
        "https://www.googleapis.com/oauth2/v1/userinfo", 
        headers={"Authorization": f"Bearer {access_token}"}
    )
    return user_info.json()

@router.get("/token")
async def get_token(token: str = Depends(oauth2_scheme)):
    return decode(token, getenv("GOOGLE_CLIENT_SECRET"), algorithms=["HS256"])
