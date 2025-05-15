# Import Python libraries
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from tortoise.contrib.fastapi import register_tortoise
import pytz
from contextlib import asynccontextmanager
from os import getenv

# Import environment variables
import lib.core.env
from config.core.settings import get_settings
from config.core.tortoise_db import TORTOISE_ORM, init_db, close_db
from config.core.redis_manager import RedisManager

# Import project modules
from app.api import *

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Redis already initialized during import
    yield
    await RedisManager.disconnect()
    await close_db()

# Create FastAPI app
app = FastAPI(
    title="API",
    description="ASGI FastAPI backend app",
    openapi_tags=[
        {"name": "Authentication", "description": "Token and social login endpoints"},
        {"name": "Sign Up", "description": "Sign up endpoints"},
        {"name": "Users API", "description": "User, account, plan, and subscription management endpoints"},
    ],
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan
)

# Add security schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")
app.swagger_ui_init_oauth = {
    "usePkceWithAuthorizationCodeGrant": True,
    "additionalQueryStringParams": {"token_type": "bearer"}
}

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Tortoise ORM with FastAPI
pytz.timezone('America/Sao_Paulo')
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,
    add_exception_handlers=True,
)

# Include API routers
for router_name in dir():
    if router_name.endswith('_router') and isinstance(globals()[router_name], APIRouter):
        app.include_router(globals()[router_name])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
