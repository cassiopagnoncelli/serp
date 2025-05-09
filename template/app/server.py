# Import Python libraries
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer

# Import environment variables
import lib.core.env
from os import getenv

# Import project modules
from app.api import *

# Create FastAPI app
app = FastAPI(
    title="API",
    openapi_tags=[
        {"name": "Users API", "description": "User management endpoints"},
        {"name": "Authentication", "description": "Authentication endpoints"}
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

# Include API routers
for router_name in dir():
    if router_name.endswith('_router') and isinstance(globals()[router_name], APIRouter):
        app.include_router(globals()[router_name])

# Mount static files
app.mount("/public", StaticFiles(directory="public"), name="public")
