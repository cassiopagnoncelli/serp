from tortoise import Tortoise
from lib.core.database.dbstring import parse_db_url
from config.core.settings import get_settings

settings = get_settings()

# Fetch DATABASE_URL and adjusting protocol.
db_url = settings.fetch("DATABASE_URL")
db_url = db_url.replace("postgresql://", "postgres://")

TORTOISE_MODELS = ["app.models", "aerich.models"]

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
    "timezone": "UTC"
}

async def init_db():
    Tortoise.init_models(TORTOISE_MODELS, "models")
    await Tortoise.init(config=TORTOISE_ORM)

async def close_db():
    await Tortoise.close_connections()
