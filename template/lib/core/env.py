from pathlib import Path
from dotenv import load_dotenv
import os

# Define app environment
APP_ENV = os.getenv('APP_ENV') or 'development'
if APP_ENV not in ['development', 'test', 'staging', 'production']:
  raise ValueError(f"Invalid app environment: {APP_ENV}")

# Load environment variables from file
env_file = Path().absolute() / f".env.{APP_ENV}"
if env_file.exists():
  load_dotenv(dotenv_path = env_file)
else:
  raise FileNotFoundError(f"Instead of using .env environment file, please use .env.{APP_ENV} file")

# Define app environment variables
is_development = APP_ENV == 'development'
is_test = APP_ENV == 'test'
is_staging = APP_ENV == 'staging'
is_production = APP_ENV == 'production'
