import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from tortoise import Tortoise
from tortoise.exceptions import DBConnectionError
from aerich import Command

from config.core.tortoise_db import TORTOISE_ORM

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def get_db_connection() -> AsyncGenerator[None, None]:
    """Context manager for database connection."""
    try:
        await Tortoise.init(config=TORTOISE_ORM)
        yield
    except DBConnectionError as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise
    finally:
        await Tortoise.close_connections()

async def check_aerich_table_exists() -> bool:
    """Check if aerich table exists in the database."""
    try:
        await Tortoise.get_connection("default").execute_query("SELECT 1 FROM aerich LIMIT 1")
        return True
    except Exception as e:
        logger.debug(f"Aerich table check failed: {str(e)}")
        return False

async def initialize_db() -> None:
    """Initialize the database with aerich."""
    try:
        command = Command(tortoise_config=TORTOISE_ORM, app='models')
        await command.init()
        # Generate schemas after initialization
        await Tortoise.generate_schemas()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise

async def upgrade_existing_db() -> None:
    """Upgrade existing database schema."""
    try:
        command = Command(tortoise_config=TORTOISE_ORM, app='models')
        # First try to create a migration
        try:
            await command.migrate()
            logger.info("Created new migration")
        except Exception as e:
            logger.debug(f"No new migrations needed: {str(e)}")
        
        # Then try to upgrade
        try:
            await command.upgrade()
            logger.info("Applied migrations successfully")
        except Exception as e:
            logger.debug(f"No migrations to apply: {str(e)}")
        
        # Always ensure schemas are up to date
        await Tortoise.generate_schemas()
        logger.info("Database upgraded successfully")
    except Exception as e:
        logger.error(f"Failed to upgrade database: {str(e)}")
        raise

async def load_schema() -> None:
    """Main function to load or upgrade database schema."""
    async with get_db_connection():
        try:
            if not await check_aerich_table_exists():
                logger.info("Initializing new database...")
                await initialize_db()
            else:
                logger.info("Upgrading existing database...")
                await upgrade_existing_db()
            logger.info("Schema management completed successfully")
        except Exception as e:
            logger.error(f"Schema management failed: {str(e)}")
            raise

def main() -> None:
    """Entry point for the script."""
    try:
        asyncio.run(load_schema())
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
