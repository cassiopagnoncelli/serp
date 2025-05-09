"""
Routers package that exports all routers from submodules.
"""
# Core.
from lib.core.api.health_check import router as health_check_router
from lib.core.api.mailer import router as mailer_router
from app.api.auth.token import router as token_router
from app.api.auth.google import router as google_router
from app.api.auth.facebook import router as facebook_router
from app.api.public.signup import router as signup_router

# Users.
from .secure.user import router as user_router

# Add all models you want to export here
__all__ = [
  "health_check_router",
  "mailer_router",
  "token_router",
  "google_router",
  "user_router",
  "signup_router",
  "facebook_router"
]
