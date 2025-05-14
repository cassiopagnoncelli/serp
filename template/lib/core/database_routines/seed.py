import os
import yaml
from pathlib import Path
from tortoise import Tortoise
from typing import Dict, Any

from config.core.tortoise_db import init_db, close_db
from config.core.settings import get_settings
from lib.core.record.inflection import to_class_name
from app.models import *

settings = get_settings()

async def load_fixtures():
    """
    Load fixtures from YAML files in db/fixtures/[APP_ENV]/*.yaml
    and insert them into the database.
    """
    env = settings.fetch('APP_ENV')
    
    # Get the fixtures directory path from project root
    fixtures_dir = Path.cwd() / 'db' / 'fixtures' / env
    
    if not fixtures_dir.exists():
        print(f"Fixtures directory not found: {fixtures_dir}")
        return
    
    # Get all YAML files in the fixtures directory
    yaml_files = list(fixtures_dir.glob('*.yaml'))
    
    if not yaml_files:
        print(f"No YAML files found in {fixtures_dir}")
        return
    
    for yaml_file in yaml_files:
        print(f"Processing {yaml_file.name}...")
        
        # Get model name from filename (e.g., users.yaml -> User)
        model_name = to_class_name(yaml_file.stem)
        
        try:
            # Get the model class
            model = globals()[model_name]
            
            # Read and parse YAML file
            with open(yaml_file, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data:
                print(f"No data found in {yaml_file.name}")
                continue
            
            # Each key in the YAML file represents a record
            for record_data in data.values():
                await model.create(**record_data)
            
            print(f"Inserted {len(data)} records into {model_name}")
            
        except KeyError:
            print(f"Model class {model_name} not found in app.models")
        except Exception as e:
            print(f"Error processing {yaml_file.name}: {str(e)}")

async def run_seeds():
    """
    Run the seed script.
    """
    try:
        await load_fixtures()
        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error during seeding: {str(e)}")

if __name__ == "__main__":
    import asyncio
    
    async def init():
        # Initialize database using the configuration
        await init_db()
        
        # Run the seeds
        await run_seeds()
        
        # Close the connection
        await close_db()
    
    asyncio.run(init())
