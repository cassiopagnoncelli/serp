from tortoise import Tortoise
import sys
from pathlib import Path
from lib.core.database.dbstring import parse_db_url

from config.core.settings import get_settings

settings = get_settings()

db_url = settings.fetch("DATABASE_URL")
db_url = db_url.replace("postgresql://", "postgres://")

TORTOISE_MODELS = ["app.models", "aerich.models"]

DEFAULT_TIMEOUT = 10

TORTOISE_ORM = {
    "connections": {
        "default": db_url
    },
    "apps": {
        "models": {
            "models": TORTOISE_MODELS,
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "UTC",
    "db_url": db_url,
    "db_type": "postgres",
    "db_params": {
        "timezone": "UTC",
        "use_tz": False,
        "timeout": DEFAULT_TIMEOUT,
        "command_timeout": DEFAULT_TIMEOUT
    }
}

async def init_db():
    """Initialize database connection with better error handling for missing modules."""
    try:
        Tortoise.init_models(TORTOISE_MODELS, "models")
        await Tortoise.init(config=TORTOISE_ORM)
        return True
    except ModuleNotFoundError as e:
        print(f"Warning: Database module missing: {e}")
        # If it's a module not found error, we can continue without database
        return False
    except Exception as e:
        print(f"Database initialization error: {e}")
        return False

async def close_db():
    """Close database connections with error handling."""
    try:
        if Tortoise._inited:
            await Tortoise.close_connections()
        return True
    except Exception as e:
        print(f"Error closing database connections: {e}")
        return False
