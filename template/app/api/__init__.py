"""
Routers package that exports all routers from submodules.
"""
from .health_check import router as health_check_router
from .users import router as users_router
from .auth import router as auth_router
from .oauth_google import router as oauth_google_router

# Add all models you want to export here
__all__ = [
  "health_check_router",
  "users_router",
  "auth_router",
  "oauth_google_router"
]
