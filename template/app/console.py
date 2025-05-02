def print_colored_snake():
  GREEN = "\033[32m"
  RED = "\033[31m"
  RESET = "\033[0m"
  snake = [
      "",
      "           " + GREEN + "   /^\\/^\\",
      "          _|__|  O|" + RESET + RED + "o o" + GREEN + "|",
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
  
  # Import all modules
  from sqlmodel import Session, SQLModel, select, update

  from app.jobs import *
  from app.models import *
  from app.services import *
  from app.utils import *
  from config.initializers.database import engine

  # Start IPython REPL
  from IPython import embed
  print("\nType 'exit()' or ^D to quit\n")

  with Session(engine) as session:
    embed()
