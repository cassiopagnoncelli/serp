# from fastapi import Depends
# from datetime import timedelta, datetime, timezone
# from sqlmodel import select
# from jwt import encode
# import bcrypt

# from app.schemas.user import UserTokenizable
# from app.models.user import User
# from config.core.settings import get_settings
# from config.core.database import SessionDep

# settings = get_settings()

# ALGORITHM: str = "HS256"
# SECRET_KEY: str = settings.fetch("ACCESS_TOKEN_SECRET_KEY")
# ACCESS_TOKEN_EXPIRE_MINUTES: int = settings.fetch("ACCESS_TOKEN_EXPIRE_MINUTES")

# class Authentication:
#   pwd_context = CryptContext(schemes = ["bcrypt"], deprecated = "auto")

#   def hash_password(self, password: str) -> str:
#     return self.pwd_context.hash(password)

#   def verify_password(self, plain_password: str, hashed_password: str) -> bool:
#     return self.pwd_context.verify(plain_password, hashed_password)

#   def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
#     to_encode = data.copy()
#     if expires_delta:
#       expire = datetime.now(timezone.utc) + expires_delta
#     else:
#       expire = datetime.now(timezone.utc) + timedelta(minutes = 15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
#     return encoded_jwt


# def hash_password2(self, password: str) -> str:
#     salt = bcrypt.gensalt()
#     return bcrypt.hashpw(password.encode(), salt).decode()

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return bcrypt.checkpw(plain_password.encode(), hashed_password.encode())

# # Find, Authenticate, and Generate Token
# def find_user_by_email(email: str, session: SessionDep = Depends(SessionDep)) -> UserTokenizable:
#     statement = select(User).where(User.email == email)
#     return session.exec(statement).first()

# def authenticate_user(email: str, password: str, session: SessionDep = Depends(SessionDep)) -> UserTokenizable:
#   user = find_user_by_email(email, session)
#   if not user:
#     return None
#   if not verify_password(password, user.hashed_password):
#     return None
#   return user

# def create_access_token(data: dict, expires_delta: timedelta | None = None):
#   to_encode = data.copy()
#   if expires_delta:
#     expire = datetime.now(timezone.utc) + expires_delta
#   else:
#     expire = datetime.now(timezone.utc) + timedelta(minutes = 15)
#   to_encode.update({"exp": expire})
#   encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
#   return encoded_jwt


# def create_access_token(email: str, session: SessionDep = Depends(SessionDep), expires_minutes: int | None = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
#   user = find_user_by_email(email, session)
#   if not user:
#     return None

#   if expires_minutes is None:
#     expires_minutes = ACCESS_TOKEN_EXPIRE_MINUTES

#   access_token_expires = datetime.now(timezone.utc) + timedelta(minutes = expires_minutes)
#   data = {
#     "id": user.id,
#     "uuid": user.uuid,
#     "name": user.name,
#     "email": user.email,
#     "status": user.status,
#     "login_provider": user.login_provider
#   }
#   access_token = jwt.encode(
#     {
#       "data": data,
#       "exp": access_token_expires
#     },
#     SECRET_KEY,
#     algorithm=ALGORITHM
#   )

#   return access_token

# def get_user(db, username: str):
#   if username in db:
#     user_dict = db[username]
#     return UserInDB(**user_dict)

# def authenticate_user(fake_db, username: str, password: str):
#   user = get_user(fake_db, username)
#   if not user:
#     return False
#   if not verify_password(password, user.hashed_password):
#     return False
#   return user
