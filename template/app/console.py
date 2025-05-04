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
  import sys
  import os
  
  # Add the project root to Python path
  project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
  sys.path.insert(0, project_root)
  
  print_colored_snake()
  
  # Import Python libraries
  from sqlmodel import SQLModel, select, update

  # Import environment variables
  import lib.core.env
  from os import getenv

  # Import project modules
  from app.jobs import *
  from app.models import *
  from app.services import *
  from app.utils import *

  # Import project initializers
  from config.initializers.database import get_session_standalone
  from config.initializers.redis import RedisStandaloneDep

  # Start IPython REPL
  from IPython import embed
  from IPython.terminal.interactiveshell import TerminalInteractiveShell
  TerminalInteractiveShell.banner1 = ""
  TerminalInteractiveShell.banner2 = ""
  print("\nType 'exit()' or ^D to quit\n")

  with RedisStandaloneDep() as redis:
    with get_session_standalone() as db:
      embed(ipython=True, no_confirm_exit=True, no_banner=True, display_banner=False)
