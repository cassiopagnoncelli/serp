import os
from sqlalchemy import create_engine
import psycopg2
import sqlalchemy

from config.core.settings import get_settings
from lib.core.env import APP_ENV
from lib.core.database.dbstring import parse_db_url

if __name__ == "__main__":
    # App settings.
    settings = get_settings()
    parsed_config = parse_db_url(settings.fetch("DATABASE_URL"))

    # Drop the target database except for production
    if APP_ENV == "production":
        raise ValueError("Cannot drop production database for security reasons, drop it manually")
    if APP_ENV not in ["development", "test", "staging"]:
        raise ValueError(f"Invalid app environment: {APP_ENV}")

    # Drop the database
    if parsed_config["driver"] in ["sqlite", "sqlite3"]:
        # For SQLite, just delete the file
        if parsed_config["path"] and os.path.exists(parsed_config["path"]):
            os.remove(parsed_config["path"])
            print(f"SQLite database file '{parsed_config['path']}' deleted successfully")
        else:
            print(f"SQLite database file '{parsed_config['path']}' not found")
    elif parsed_config["driver"] == "postgresql":
        # Connect to postgres database to drop the target database
        conn = psycopg2.connect(
            dbname="postgres",
            user=parsed_config["username"],
            password=parsed_config["password"],
            host=parsed_config["host"],
            port=parsed_config["port"]
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (parsed_config["dbname"],))
        db_exists = cursor.fetchone() is not None

        # Terminate all connections to the target database
        cursor.execute(f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{parsed_config["dbname"]}'
            AND pid <> pg_backend_pid();
        """)
        
        # Drop the database
        cursor.execute(f'DROP DATABASE IF EXISTS "{parsed_config["dbname"]}"')
        cursor.close()
        conn.close()
        
        if db_exists:
            print(f"PostgreSQL database '{parsed_config['dbname']}' dropped successfully")
        else:
            print(f"PostgreSQL database '{parsed_config['dbname']}' did not exist")
    else:
        raise ValueError(f"Unsupported database driver: {parsed_config['driver']}")
