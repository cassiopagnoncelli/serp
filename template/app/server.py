from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import *

app = FastAPI(title="API")

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

for router_name in dir():
  if router_name.endswith('_router') and isinstance(globals()[router_name], APIRouter):
    app.include_router(globals()[router_name])

app.mount("/public", StaticFiles(directory="public"), name="public")
