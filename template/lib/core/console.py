import sys
import os
from os import getenv
from pathlib import Path
import pprint

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
from config.core.database import get_session_standalone
from config.core.redis import RedisStandaloneDep
from config.core.storage import get_storage
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
  c.TerminalInteractiveShell.editing_mode = "vi"  # Optional: vi mode
  c.InteractiveShell.pretty = True
  c.InteractiveShell.pretty_indent = 3  # Set indentation to 3 spaces
  return c

def setup_ipython_history():
  ipython_dir = Path.home() / ".config" / "serp-ipython"
  ipython_dir.mkdir(parents=True, exist_ok=True)
  os.environ["IPYTHONDIR"] = str(ipython_dir)

def start_console():
  print_colored_snake()
  print("\n💻 Starting interactive console. Type 'exit()' or press Ctrl-D to quit.\n")

  config = create_ipython_config()
  setup_ipython_history()  
  with RedisStandaloneDep() as redis:
    with get_session_standalone() as db:
      shell = InteractiveShellEmbed(config=config, banner1="📦 Console loaded", exit_msg="👋 Goodbye!")
      
      # Register the custom formatter after shell is created
      shell.display_formatter.formatters['text/plain'].for_type(dict, custom_dict_formatter)
      
      shell(local_ns = {
        "db": db,
        "redis": redis,
        "storage": get_storage()
      })

if __name__ == "__main__":
  start_console()
