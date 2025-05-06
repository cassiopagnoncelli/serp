# import sys
# import os

# sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# from sqlmodel import Session, SQLModel
# from config.core.database import get_session_standalone, engine

# with get_session_standalone() as db:
#   SQLModel.metadata.create_all(engine)


import os
from sqlalchemy import create_engine
import psycopg2
import sqlalchemy

from config.core.settings import get_settings
from lib.core.env import APP_ENV
from lib.core.dbstring import parse_db_url

def create_database_if_not_exists(parsed_config):
    """Create database if it doesn't exist."""
    if parsed_config['driver'] == 'postgresql':
        # For PostgreSQL, we need to connect to a default database first
        default_db_url = f"postgresql://{parsed_config['username']}:{parsed_config['password']}@{parsed_config['host']}:{parsed_config['port']}/postgres"
        conn = psycopg2.connect(default_db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (parsed_config['dbname'],))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f'CREATE DATABASE {parsed_config["dbname"]}')
            print(f"Created database {parsed_config['dbname']}")
        else:
            print(f"Database {parsed_config['dbname']} already exists")
            
        cursor.close()
        conn.close()
        
    elif parsed_config['driver'] == 'sqlite':
        # For SQLite, we just need to check if the file exists
        db_path = parsed_config['path']
        if not os.path.exists(db_path):
            # Create an empty file to initialize the database
            with open(db_path, 'w') as f:
                pass
            print(f"Created SQLite database at {db_path}")
        else:
            print(f"SQLite database at {db_path} already exists")
    else:
        raise ValueError(f"Unsupported database driver: {parsed_config['driver']}")

if __name__ == "__main__":
    # App settings.
    settings = get_settings()
    parsed_config = parse_db_url(settings.fetch("DATABASE_URL"))
    
    # Create database if it doesn't exist
    create_database_if_not_exists(parsed_config)
