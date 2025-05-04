import sys
import os
from os import getenv
from pathlib import Path

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

import lib.core.env

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

if __name__ == "__main__":
  from IPython.terminal.embed import InteractiveShellEmbed
  from traitlets.config import Config
  from sqlmodel import SQLModel, select, update

  # Import project initializers
  from config.initializers.database import get_session_standalone
  from config.initializers.redis import RedisStandaloneDep
  from config.initializers.storage import *

  # Import project modules
  from app.jobs import *
  from app.models import *
  from app.services import *
  from app.utils import *

  print_colored_snake()

  c = Config()
  c.TerminalInteractiveShell.confirm_exit = False
  c.InteractiveShell.ast_node_interactivity = "last_expr"
  c.InteractiveShell.pprint = True
  c.InteractiveShellEmbed.colors = "Linux"        # 'NoColor', 'LightBG', 'Linux'
  c.InteractiveShellEmbed.autocall = 2            # Auto-call functions (like Rails console)
  c.TerminalInteractiveShell.editing_mode = "vi"  # Optional: vi mode

  # Setup history (save command history between sessions)
  ipython_dir = Path.home() / ".config" / "serp-ipython"
  ipython_dir.mkdir(parents=True, exist_ok=True)
  os.environ["IPYTHONDIR"] = str(ipython_dir)

  # Start IPython REPL
  print("\n💻 Starting interactive console. Type 'exit()' or press Ctrl-D to quit.\n")
  with RedisStandaloneDep() as redis:
    with get_session_standalone() as db:
      shell = InteractiveShellEmbed(config=c, banner1="📦 Console loaded", exit_msg="👋 Goodbye!")
      shell(local_ns = {
        "db": db,
        "redis": redis
      })
