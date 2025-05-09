from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, SQLModel, select, update
from datetime import datetime, timedelta
import random
import string

from app.models import User, Token, UserStatus
from app.schemas.user import UserTokenizable
from config.core.settings import get_settings
from config.core.database import SessionDep
from lib.core.authentication.passwords import verify_password
from lib.core.authentication.tokens import generate_access_token, decode_access_token

settings = get_settings()

SECRET_KEY: str = settings.fetch("ACCESS_TOKEN_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(settings.fetch("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
bearer_scheme = HTTPBearer()

def find_user_by_email(email: str, session: SessionDep = Depends(SessionDep)) -> UserTokenizable:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()

def authenticate_user(email: str, password: str, session: SessionDep = Depends(SessionDep)) -> UserTokenizable:
    user = find_user_by_email(email, session)
    if not user:
        return None
    if not verify_password(password, user.enc_password):
        return None
    return user

def generate_user_token(data: dict, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    user_data = {
      "id": data["id"],
      "uuid": data["uuid"],
      "account_uuid": data["account_uuid"],
      "email": data["email"],
      "name": data["name"],
      "status": data["status"],
      "login_provider": data["login_provider"],
      "created_at": data["created_at"]
    }
    return generate_access_token(data=user_data, secret_key=SECRET_KEY, expires_minutes=expires_minutes)

def decode_user_token(token: str) -> dict:
    data = decode_access_token(token=token, secret_key=SECRET_KEY)
    return data["data"] if data else None

def persist_user_token(
      user_id: int,
      token: str,
      expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
      ip_address: str = None,
      user_agent: str = None,
      location: dict = None,
      device: dict = None,
      session: SessionDep = Depends(SessionDep)
  ) -> Token:
    obj = Token(
      user_id=user_id,
      token=token,
      expires_at=datetime.now() + timedelta(minutes=expires_minutes),
      ip_address=ip_address,
      user_agent=user_agent,
      location=location,
      device=device
    )
    session.add(obj)
    session.commit()
    return obj

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

def login_user_with_password(
      email: str,
      password: str,
      expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
      ip_address: str = None,
      user_agent: str = None,
      location: dict = None,
      device: dict = None,
      session: SessionDep = Depends(SessionDep)
  ) -> str:
    user = authenticate_user(email, password, session)
    if not user:
        return None
    if user.status != UserStatus.active:
      raise HTTPException(status_code=401, detail="User is not active")
    token = generate_user_token(user.model_dump(), expires_minutes)
    persist_user_token(user.id, token, expires_minutes, ip_address, user_agent, location, device, session)
    return token

def random_password() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=16))

def login_user_with_google(
      email: str,
      expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
      ip_address: str = None,
      user_agent: str = None,
      location: dict = None,
      device: dict = None,
      session: SessionDep = Depends(SessionDep)
  ) -> str:
    user = find_user_by_email(email, session)
    if not user:
        return None
    token = generate_user_token(user.model_dump(), expires_minutes)
    persist_user_token(user.id, token, expires_minutes, ip_address, user_agent, location, device, session)
    return token

def login_user_with_facebook(
      email: str,
      expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
      ip_address: str = None,
      user_agent: str = None,
      location: dict = None,
      device: dict = None,
      session: SessionDep = Depends(SessionDep)
  ) -> str:
    user = find_user_by_email(email, session)
    if not user:
        return None
    token = generate_user_token(user.model_dump(), expires_minutes)
    persist_user_token(user.id, token, expires_minutes, ip_address, user_agent, location, device, session)
    return token
