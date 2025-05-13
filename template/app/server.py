# Import Python libraries
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer
from tortoise.contrib.fastapi import register_tortoise

# Import environment variables
import lib.core.env
from os import getenv
from config.core.database import TORTOISE_ORM

# Import project modules
from app.api import *

# Create FastAPI app
app = FastAPI(
    title="API",
    description="ASGI FastAPI backend app",
    openapi_tags=[
        {"name": "Authentication", "description": "Token and social login endpoints"},
        {"name": "Sign Up", "description": "Sign up endpoints"},
        {"name": "Users API", "description": "User, account, plan, and subscription management endpoints"},
    ],
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

# Add security schemes
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
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
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,
    add_exception_handlers=True,
)

# Include API routers
for router_name in dir():
    if router_name.endswith('_router') and isinstance(globals()[router_name], APIRouter):
        app.include_router(globals()[router_name])

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")
