import sys
import os
from os import getenv
from pathlib import Path
import pprint
import concurrent.futures
import threading
import time
import asyncio
from asyncio import run as sync_run
from redis import Redis

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

# Load .env
import lib.core.env

# IPython imports
from IPython.terminal.embed import InteractiveShellEmbed
from traitlets.config import Config
from IPython.lib.pretty import pprint as ipprint
from IPython import get_ipython

# Project imports
from config.core.tortoise_db import init_db, close_db, TORTOISE_ORM
from config.core.redis_manager import RedisManager
from config.core.storage import get_storage, storage_config
from config.core.feature_flags import get_feature_flags
from config.core.settings import get_settings
from lib.core.storage.main import Storage
from lib.core.console.pretty_print import pp, PrettyPrinter
from lib.core.console.service_status import ServiceStatus, PENDING, SUCCESS, ERROR, LOADING
from lib.core.redis_service import SyncRedisAdapter
from lib.core.database.sync_tortoise_adapter import SyncTortoiseAdapter, get_tortoise_adapter
from lib.core.dt import *
from app.jobs import *
from app.models import *
from app.services import *
from app.utils import *

def print_colored_snake():
  GREEN = "\033[32m"
  RED = "\033[31m"
  RESET = "\033[0m"
  snake = [
    "",
    "           " + GREEN + "   /^\\/^\\",
    "          _|__| " + RED + "o o" + GREEN + " |",
    " \\/     /~     \\_/ \\",
    "  \\____|__________/  \\",
    "         \\_______      \\",
    "                 `\\     \\                 \\",
    "                   |     |                  \\",
    "                  /      /                    \\",
    "                 /     /                       \\\\",
    "               /      /                         \\ \\",
    "              /     /                            \\  \\",
    "            /     /             _----_            \\   \\",
    "           /     /           _-~      ~-_         |   |",
    "          (      (        _-~    _--_    ~-_     _/   |",
    "           \\      ~-____-~    _-~    ~-_    ~-_-~    /",
    "             ~-_           _-~          ~-_       _/",
    "                ~--______-~                ~-___-~" + RESET,
    ""
  ]
  for line in snake:
      print(line)

def format_dict(d, indent=0):
  result = []
  for key, value in d.items():
    if isinstance(value, dict):
      result.append(f"{' ' * indent}\033[1;37m{key}\033[0m:")
      result.extend(format_dict(value, indent + 3))
    else:
      result.append(f"{' ' * indent}\033[1;37m{key}\033[0m: {value}")
  return result

def custom_dict_formatter(obj, p, cycle):
  if isinstance(obj, dict):
    if cycle:
      p.text('{...}')
      return
    
    formatted = format_dict(obj)
    p.text('\n'.join(formatted))

def create_ipython_config():
  c = Config()
  c.TerminalInteractiveShell.confirm_exit = False
  c.InteractiveShell.ast_node_interactivity = "last_expr"
  c.InteractiveShell.pprint = True
  c.InteractiveShellEmbed.colors = "Linux"        # 'NoColor', 'LightBG', 'Linux'
  c.InteractiveShellEmbed.autocall = 2            # Auto-call functions (like Rails console)
  c.InteractiveShell.pretty = True
  c.InteractiveShell.pretty_indent = 3  # Set indentation to 3 spaces
  c.TerminalIPythonApp.display_banner = False     # Hide the banner
  c.InteractiveShellEmbed.display_banner = False  # Hide the banner for embedded shell too
  return c

def setup_ipython_history():
  ipython_dir = Path.home() / ".config" / "serp-ipython"
  ipython_dir.mkdir(parents=True, exist_ok=True)
  os.environ["IPYTHONDIR"] = str(ipython_dir)

def initialize_storage(status_manager):
  """Initialize storage with timeout and fallback."""
  try:
    status_manager.update_storage(LOADING)
    
    # Make sure local storage directory exists if using local driver
    if storage_config.get('driver') == 'local':
      local_path = Path(storage_config.get('url_endpoint', 'tmp/storage'))
      local_path.mkdir(parents=True, exist_ok=True)
    
    # Use threading.Timer instead of signals for timeout (works in threads)
    storage = None
    storage_initialized = threading.Event()
    storage_error = [None]  # Use a list to store the error (if any)
    
    def initialize():
      try:
        nonlocal storage
        storage = get_storage()
        storage_initialized.set()
      except Exception as e:
        storage_error[0] = e
        storage_initialized.set()
    
    # Start initialization in a thread
    init_thread = threading.Thread(target=initialize)
    init_thread.daemon = True
    init_thread.start()
    
    # Wait for initialization with timeout
    if storage_initialized.wait(timeout=5):
      # Check if we got an error
      if storage_error[0] is not None:
        raise storage_error[0]
      status_manager.update_storage(SUCCESS)
      return storage
    else:
      # Timeout occurred
      local_path = Path("tmp/storage")
      local_path.mkdir(parents=True, exist_ok=True)
      storage = Storage({
        'driver': 'local',
        'url_endpoint': str(local_path)
      })
      status_manager.update_storage(SUCCESS)
      return storage
      
  except Exception as e:
    # Create a minimal local storage instance as fallback
    try:
      local_path = Path("tmp/storage")
      local_path.mkdir(parents=True, exist_ok=True)
      storage = Storage({
        'driver': 'local',
        'url_endpoint': str(local_path)
      })
      status_manager.update_storage(SUCCESS)
      return storage
    except Exception as local_error:
      status_manager.update_storage(ERROR)
      return None

def initialize_db(status_manager):
  """Initialize database session."""
  try:
    status_manager.update_db(LOADING)
    
    # Initialize Tortoise ORM
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_db())
    
    # Create a namespace with the database connection and sync adapter
    db = {
      'close': lambda: loop.run_until_complete(close_db()),
      'sync': get_tortoise_adapter()
    }
    
    status_manager.update_db(SUCCESS)
    return db
  except Exception as e:
    status_manager.update_db(ERROR)
    return None

def initialize_redis(status_manager):
  """Initialize Redis connection."""
  try:
    status_manager.update_redis(LOADING)
    # Create a synchronous adapter for the async RedisManager
    redis = SyncRedisAdapter()
    # Test the connection
    redis.ping()
    # Also provide the async RedisManager class directly
    _redis = RedisManager
    async_redis = RedisManager
    status_manager.update_redis(SUCCESS)
    return {'redis': redis, '_redis': _redis, 'async_redis': async_redis}
  except Exception as e:
    status_manager.update_redis(ERROR)
    return None

def start_console():
  print_colored_snake()
  print("\n💻 Starting interactive console. Type 'exit()' or press Ctrl-D to quit.\n")
  
  config = create_ipython_config()
  setup_ipython_history()
  
  # Create status manager
  status_manager = ServiceStatus()
  
  # Initialize services asynchronously
  services = {}
  def init_services():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
      # Submit all initialization tasks
      storage_future = executor.submit(initialize_storage, status_manager)
      db_future = executor.submit(initialize_db, status_manager)
      redis_future = executor.submit(initialize_redis, status_manager)
      
      # Get results as they complete
      services['storage'] = storage_future.result()
      services['db'] = db_future.result()
      redis_result = redis_future.result()
      if redis_result:
        services.update(redis_result)
  
  # Run initialization in a separate thread
  init_thread = threading.Thread(target=init_services)
  init_thread.start()
  init_thread.join()  # Wait for initialization to complete
  
  # Finalize the status display
  status_manager.finalize()
  
  # Create the shell
  shell = InteractiveShellEmbed(config=config, banner1="", exit_msg="👋 Goodbye!")
  
  # Register the custom formatter after shell is created
  shell.display_formatter.formatters['text/plain'].for_type(dict, custom_dict_formatter)
  
  # Create a namespace with available services
  namespace = {}
  
  # Add services that were successfully initialized
  for name, service in services.items():
    if service is not None:
      namespace[name] = service

  # Add configurations
  namespace['feature_flags'] = get_feature_flags()
  namespace['settings'] = get_settings()
  
  # Add pretty printer function to namespace
  namespace['pp'] = pp
  
  # Create direct model access
  if services.get('db') and services['db'].get('sync'):
    # Get the Models adapter
    models_adapter = services['db']['sync']
    
    # Import all models and add them directly to the namespace
    from app.models import __all__ as model_names
    for model_name in model_names:
      try:
        # Add the model directly to the namespace
        namespace[model_name] = models_adapter.get_model(f'models.{model_name}')
      except Exception as e:
        pass  # Skip if model can't be loaded
  
  # Start the shell with the namespace
  shell(local_ns=namespace)

if __name__ == "__main__":
  start_console()
