"""
Routers package that exports all routers from submodules.
"""
# Core.
from lib.core.api.health_check import router as health_check_router
from lib.core.api.mailer import router as mailer_router
from app.api.auth.token import router as token_router
from app.api.auth.google import router as google_router

# Users.
from .secure.users import router as users_router

# Add all models you want to export here
__all__ = [
  "health_check_router",
  "mailer_router",
  "token_router",
  "google_router",
  "users_router"
]
