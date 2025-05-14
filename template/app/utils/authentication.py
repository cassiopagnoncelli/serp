from fastapi import Depends, HTTPException, Security
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from datetime import timedelta
import random
import string

from lib.core.authentication.passwords import verify_password
from lib.core.authentication.tokens import generate_access_token, decode_access_token
from lib.core.dt import DateTime
from config.core.settings import get_settings
from app.models.user import *
from app.models.token import *
from app.schemas.user import *
from app.schemas.token import TokenSchema, CreateTokenSchema

settings = get_settings()

SECRET_KEY: str = settings.fetch("ACCESS_TOKEN_SECRET_KEY")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(settings.fetch("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
bearer_scheme = HTTPBearer()

async def find_user_by_email(email: str) -> UserTokenizable:
    return await User.filter(email=email).first()

async def authenticate_user(email: str, password: str) -> UserTokenizable:
    user = await find_user_by_email(email)
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
      "created_at": data["created_at"],
      "updated_at": data["updated_at"],
      "enc_password": data["enc_password"]
    }
    return generate_access_token(data=user_data, secret_key=SECRET_KEY, expires_minutes=expires_minutes)

def decode_user_token(token: str) -> dict:
    data = decode_access_token(token=token, secret_key=SECRET_KEY)
    return data if data else None

async def persist_user_token(
      user_id: int,
      token: str,
      expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
      ip_address: str = None,
      user_agent: str = None,
      location: dict = None,
      device: dict = None,
  ) -> TokenSchema:
    expires_at = DateTime.utc() + timedelta(minutes=expires_minutes)
    
    # Create and validate the data using CreateTokenSchema
    token_data = CreateTokenSchema(
        user_id=user_id,
        token=token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
        location=location,
        device=device
    )
    
    # Create the Token model instance with validated data
    tok = Token(
        user_id=token_data.user_id,
        token=token_data.token,
        expires_at=token_data.expires_at,
        ip_address=token_data.ip_address,
        user_agent=token_data.user_agent,
        location=token_data.location,
        device=token_data.device
    )
    await tok.save()
    
    # Convert the saved model to TokenSchema for response
    return TokenSchema.model_validate(tok)

async def get_current_user(
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
    return UserTokenizable.model_validate(token_data)

def random_password() -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=16))

async def login_user_with_password(
      email: str,
      password: str,
      expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
      ip_address: str = None,
      user_agent: str = None,
      location: dict = None,
      device: dict = None,
  ) -> str:
    user = await authenticate_user(email, password)
    if not user:
        return None
    if user.status != UserStatus.active:
      raise HTTPException(status_code=401, detail="User is not active")
    data = user.to_dict()
    token = generate_user_token(data, expires_minutes)
    await persist_user_token(user.id, token, expires_minutes, ip_address, user_agent, location, device)
    return token

async def login_user_with_google(
      email: str,
      expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
      ip_address: str = None,
      user_agent: str = None,
      location: dict = None,
      device: dict = None,
  ) -> str:
    user = await find_user_by_email(email)
    if not user:
        return None
    data = user.to_dict()
    token = generate_user_token(data, expires_minutes)
    await persist_user_token(user.id, token, expires_minutes, ip_address, user_agent, location, device)
    return token

async def login_user_with_facebook(
      email: str,
      expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES,
      ip_address: str = None,
      user_agent: str = None,
      location: dict = None,
      device: dict = None,
  ) -> str:
    user = await find_user_by_email(email)
    if not user:
        return None
    data = user.to_dict()
    token = generate_user_token(data, expires_minutes)
    await persist_user_token(user.id, token, expires_minutes, ip_address, user_agent, location, device)
    return token
