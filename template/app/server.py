# Import Python libraries
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import environment variables
import lib.core.env
from os import getenv

# Import project modules
from app.api import *

# Create FastAPI app
app = FastAPI(title="API")

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
