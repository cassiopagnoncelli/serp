from pathlib import Path
from dotenv import load_dotenv
import os

# Define app environment
APP_ENV = os.getenv('APP_ENV') or 'development'
if APP_ENV not in ['development', 'test', 'staging', 'production']:
  raise ValueError(f"Invalid app environment: {APP_ENV}")

# Load environment variables from file
if file_exists(Path().absolute() / f".env.{APP_ENV}"):
  load_dotenv(dotenv_path = Path().absolute() / f".env.{APP_ENV}")
else:
  raise FileNotFoundError(f"Instead of using .env environment file, please use .env.{APP_ENV} file")

# Define app environment variables
app_env_development = APP_ENV == 'development'
app_env_test = APP_ENV == 'test'
app_env_staging = APP_ENV == 'staging'
app_env_production = APP_ENV == 'production'
