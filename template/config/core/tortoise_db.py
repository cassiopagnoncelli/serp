from tortoise import Tortoise

Tortoise.init_models(["app.records"], "models")

TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": "localhost",
                "port": "5432",
                "user": "cassio",
                "password": "123",
                "database": "bla_development",
            }
        }
    },
    "apps": {
        "models": {
            # "models": ["app.models", "aerich.models"],
            "models": ["app.records"],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    "timezone": "UTC"
}

async def init_db():
    await Tortoise.init(config=TORTOISE_ORM)

async def close_db():
    await Tortoise.close_connections()
