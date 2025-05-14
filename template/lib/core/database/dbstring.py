import dj_database_url
from typing import Dict, Optional

def parse_db_url(url: str) -> Dict[str, Optional[str]]:
    """
    Parse a database connection URL into its components using dj-database-url.
    
    Args:
        url: Database connection string (e.g. postgresql://user:pass@host:port/db)
        
    Returns:
        Dictionary containing the parsed components:
        - driver: Database driver (e.g. postgresql, sqlite)
        - username: Database username
        - password: Database password
        - host: Database host
        - port: Database port
        - dbname: Database name
        - path: Path (for SQLite)
    """
    config = dj_database_url.parse(url)
    
    return {
        'driver': config['ENGINE'].split('.')[-1],  # Extract just the engine name
        'username': config.get('USER'),
        'password': config.get('PASSWORD'),
        'host': config.get('HOST'),
        'port': str(config.get('PORT')) if config.get('PORT') else None,
        'dbname': config.get('NAME'),
        'path': config.get('NAME') if config['ENGINE'].endswith('sqlite3') else None
    }
