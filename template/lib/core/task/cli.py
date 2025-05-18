import sys
import os
import argparse
import pprint
import time
import threading
from typing import List, Dict, Any, Optional
import traceback

# Project root setup
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import lib.core.env
from lib.core.task.main import load_all_tasks, list_tasks, run_task, describe_task
from config.core.tortoise_db import init_db, close_db
from config.core.storage import get_storage
from config.core.redis_manager import RedisManager
import asyncio

# ANSI escape codes for formatting
BOLD = "\033[1m"
UNDERLINE = "\033[4m"
RESET = "\033[0m"

class TaskRunner:
    def __init__(self):
        self.parser = self._create_parser()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(description="Task runner for SERP application")
        subparsers = parser.add_subparsers(dest="command", help="Command to run")
        
        # List command
        list_parser = subparsers.add_parser("list", help="List available tasks")
        
        # Run command
        run_parser = subparsers.add_parser("run", help="Run a specific task")
        run_parser.add_argument("task_name", nargs='?', help="Name of the task to run")
        run_parser.add_argument("args", nargs="*", help="Arguments to pass to the task")
        run_parser.add_argument("--param", "-p", action="append", help="Key=value parameters to pass to the task")
        
        # Describe command
        describe_parser = subparsers.add_parser("describe", help="Describe a specific task")
        describe_parser.add_argument("task_name", help="Name of the task to describe")
        
        return parser
    
    def _parse_params(self, param_list: Optional[List[str]]) -> Dict[str, Any]:
        """Parse --param arguments into a dictionary."""
        params = {}
        if not param_list:
            return params
            
        for param in param_list:
            if "=" not in param:
                print(f"Warning: Ignoring malformed parameter '{param}'. Expected format: key=value")
                continue
                
            key, value = param.split("=", 1)
            # Try to convert to appropriate type (int, float, bool)
            if value.lower() == "true":
                value = True
            elif value.lower() == "false":
                value = False
            elif value.isdigit():
                value = int(value)
            elif value.replace(".", "", 1).isdigit() and value.count(".") == 1:
                value = float(value)
                
            params[key] = value
            
        return params
    
    def _format_time(self, seconds: float) -> str:
        """Format time duration based on its magnitude."""
        if seconds < 0.001:
            return f"{seconds * 1_000_000:.2f} µs"
        elif seconds < 1:
            return f"{seconds * 1_000:.2f} ms"
        elif seconds < 60:
            return f"{seconds:.2f} sec"
        elif seconds < 3600:
            minutes = int(seconds // 60)
            sec = seconds % 60
            return f"{minutes} min {sec:.2f} sec"
        else:
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            sec = seconds % 60
            return f"{hours} hr {minutes} min {sec:.2f} sec"
    
    def list_tasks_command(self) -> int:
        """List all available tasks."""
        tasks = list_tasks()
        if not tasks:
            print("No tasks found. Define tasks using the @task decorator in lib/tasks/")
            return 1
        
        # Find the longest task name for formatting
        longest_name = max(len(task["name"]) for task in tasks) if tasks else 0
        column_width = max(longest_name + 5, 25)  # Minimum 25 chars, or longest + 5
        
        # Terminal width detection (fallback to 80 if not available)
        try:
            term_width = os.get_terminal_size().columns
        except (AttributeError, OSError):
            term_width = 80
        
        # Print header in man page style
        print(f"{BOLD}TASKS(1){RESET}")
        
        print(f"\n{BOLD}NAME{RESET}")
        print("    tasks - List and describe available tasks\n")
        
        print(f"{BOLD}SYNOPSIS{RESET}")
        print("    serp tasks [task_name]\n")
        
        print(f"{BOLD}AVAILABLE TASKS{RESET}")
        
        # Format and print each task
        for task_info in sorted(tasks, key=lambda t: t["name"]):
            name = task_info["name"]
            description = task_info["description"]
            
            # Format with fixed width column for the name and bold task name
            print(f"    {BOLD}{name}{RESET}{' ' * (column_width - len(name))} {description}")
        
        print(f"\n{BOLD}DESCRIPTION{RESET}")
        print("    Tasks lists available tasks along with their brief descriptions, while")
        print("    providing a task name parameter describes the task in richer detail.")
        print()
        
        return 0
        
    def describe_task_command(self, task_name: str) -> int:
        """Describe a specific task."""
        try:
            task_info = describe_task(task_name)
            
            # Print in man page style
            print(f"{BOLD}{task_info['name']}{RESET}")
            
            print(f"\n{BOLD}NAME{RESET}")
            print(f"    {task_info['name']} - {task_info['description']}")
            
            print(f"\n{BOLD}SYNOPSIS{RESET}")
            synopsis = f"    serp task {task_info['name']}"
            for param in task_info["parameters"]:
                if param["required"]:
                    synopsis += f" <{param['name']}>"
                else:
                    synopsis += f" [{param['name']}={param['default']}]"
            print(synopsis)
            
            print(f"\n{BOLD}DESCRIPTION{RESET}")
            print(f"    {task_info['description']}")
            
            if task_info["parameters"]:
                print(f"\n{BOLD}PARAMETERS{RESET}")
                for param in task_info["parameters"]:
                    name = param["name"]
                    required = "required" if param["required"] else f"optional, default: {param['default']}"
                    print(f"    {BOLD}{name}{RESET}")
                    print(f"        {required}")
            else:
                print(f"\n{BOLD}PARAMETERS{RESET}")
                print("    This task takes no parameters.")
            
            print(f"\n{BOLD}EXAMPLES{RESET}")
            example = f"    serp task {task_info['name']}"
            if task_info["parameters"]:
                for param in task_info["parameters"]:
                    if not param["required"]:
                        continue
                    example += f" --param {param['name']}=<value>"
            example += "\n"
            print(example)
            
            if any(not p["required"] for p in task_info["parameters"]):
                print(f"\n    # With optional parameters")
                example = f"    serp task {task_info['name']}"
                for param in task_info["parameters"]:
                    if param["required"]:
                        example += f" --param {param['name']}=<value>"
                    else:
                        example += f" --param {param['name']}={param['default']}"
                example += "\n"
                print(example)
            
            return 0
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    def run_help_command(self) -> int:
        """Display help for the run command in man page style."""
        # Print header in man page style
        print(f"{BOLD}TASK-RUN(1){RESET}")
        
        print(f"\n{BOLD}NAME{RESET}")
        print("    task - Execute a specific task with parameters\n")
        
        print(f"{BOLD}SYNOPSIS{RESET}")
        print("    serp task <task_name> [--param key=value]\n")
        
        print(f"{BOLD}DESCRIPTION{RESET}")
        print("    The command executes a specific task with the given parameters.")
        print("    Tasks are defined in the application and can perform various operations.")
        
        print(f"\n{BOLD}OPTIONS{RESET}")
        print("    --param, -p   Pass parameters in the form key=value")
        
        print(f"\n{BOLD}EXAMPLES{RESET}")
        print("    serp task hello_world")
        print("    serp task greeting --param name=John")
        print("    serp task factorial --param n=10")
        print()
        
        # List available tasks as a reference
        tasks = list_tasks()
        if tasks:
            print(f"{BOLD}AVAILABLE TASKS{RESET}")
            longest_name = max(len(task["name"]) for task in tasks) if tasks else 0
            column_width = max(longest_name + 5, 25)  # Minimum 25 chars, or longest + 5
            
            for task_info in sorted(tasks, key=lambda t: t["name"]):
                name = task_info["name"]
                description = task_info["description"]
                print(f"    {BOLD}{name}{RESET}{' ' * (column_width - len(name))} {description}")
            print()
        
        return 0
    
    async def run_task_command(self, task_name: str, args: List[str], param_list: Optional[List[str]]) -> int:
        """Run a specific task."""
        start_time = time.time()
        
        try:
            # Print information about the task being run
            print(f"Running task: {BOLD}{task_name}{RESET}")
            if args:
                print(f"Arguments: {args}")
            if kwargs := self._parse_params(param_list):
                print(f"Parameters: {kwargs}")
            
            # Run the task with timing
            task_start = time.time()
            result = run_task(task_name, *args, **kwargs)
            task_end = time.time()
            task_execution_time = task_end - task_start
            
            # Print the result if there is one
            if result is not None:
                print("\nTask result:")
                pprint.pprint(result)
            
            # Print timing information
            print(f"\nTask '{BOLD}{task_name}{RESET}' completed in {BOLD}{self._format_time(task_execution_time)}{RESET}.")
                
            return 0
        except Exception as e:
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"Error running task '{BOLD}{task_name}{RESET}' (after {self._format_time(total_time)}):")
            print(f"{type(e).__name__}: {e}")
            traceback.print_exc()
            return 1
    
    async def run(self, args=None) -> int:
        """Run the task runner with the given arguments."""
        # Normal parsing for commands
        args = self.parser.parse_args(args)
        
        # Load all tasks
        load_all_tasks()
        
        # Initialize database with timeout
        await self._init_db_with_timeout(10)  # 10 second timeout
        
        # Initialize Redis with timeout
        await self._init_redis_with_timeout(10)  # 10 second timeout
        
        # Initialize Storage with timeout
        await self._init_storage_with_timeout(10)  # 10 second timeout
        
        try:
            if args.command == "list":
                return self.list_tasks_command()
            elif args.command == "describe":
                return self.describe_task_command(args.task_name)
            elif args.command == "run":
                # If no task name is provided, show run help
                if not args.task_name:
                    return self.run_help_command()
                return await self.run_task_command(args.task_name, args.args, args.param)
            else:
                self.parser.print_help()
                return 1
        finally:
            # Close connections
            await self._close_connections()
    
    async def _init_db_with_timeout(self, timeout_seconds: int = 10) -> None:
        """Initialize database connection with timeout."""
        db_initialized = threading.Event()
        db_error = [None]  # Use a list to store any errors
        db_result = [False]  # To store the initialization result
        
        # Function to run the database initialization
        def init_db_thread():
            try:
                try:
                    # First try the normal initialization with improved error handling
                    result = asyncio.run(init_db())
                    db_result[0] = result
                except ModuleNotFoundError as e:
                    # If asyncpg or other required module is missing, log it but continue
                    print(f"Warning: Database module missing: {e}")
                    # We can consider this initialized since we can continue without DB
                    db_result[0] = False
                db_initialized.set()
            except Exception as e:
                db_error[0] = e
                db_initialized.set()
        
        # Start initialization in a thread
        thread = threading.Thread(target=init_db_thread)
        thread.daemon = True
        thread.start()
        
        # Wait for initialization with timeout
        if not db_initialized.wait(timeout=timeout_seconds):
            print(f"Warning: Database initialization timed out after {timeout_seconds} seconds.")
            return
            
        # Check if we got an error
        if db_error[0] is not None:
            print(f"Warning: Database initialization failed: {db_error[0]}")
        elif not db_result[0]:
            print("Note: Running without database connection.")
        else:
            print("Database initialized successfully.")
    
    async def _init_redis_with_timeout(self, timeout_seconds: int = 10) -> None:
        """Initialize Redis connection with timeout."""
        redis_initialized = threading.Event()
        redis_error = [None]  # Use a list to store any errors
        
        # Function to run the Redis initialization
        def init_redis_thread():
            try:
                # Get Redis client with timeout
                from config.core.settings import get_settings
                
                try:
                    settings = get_settings()
                
                    # First just initialize the Redis manager without connecting
                    RedisManager.initialize(url=settings.REDIS_URL)
                    
                    # We don't actually need to test the connection for tasks
                    # Just set it as initialized
                    redis_initialized.set()
                except ModuleNotFoundError as e:
                    # If Redis modules are missing, log it but continue
                    print(f"Warning: Redis module missing: {e}")
                    redis_initialized.set()
            except Exception as e:
                redis_error[0] = e
                redis_initialized.set()
        
        # Start initialization in a thread
        thread = threading.Thread(target=init_redis_thread)
        thread.daemon = True
        thread.start()
        
        # Wait for initialization with timeout
        if not redis_initialized.wait(timeout=timeout_seconds):
            print(f"Warning: Redis initialization timed out after {timeout_seconds} seconds.")
            return
            
        # Check if we got an error
        if redis_error[0] is not None:
            print(f"Warning: Redis initialization failed: {redis_error[0]}")
    
    async def _init_storage_with_timeout(self, timeout_seconds: int = 10) -> None:
        """Initialize storage connection with timeout."""
        storage_initialized = threading.Event()
        storage_error = [None]  # Use a list to store any errors
        storage_instance = [None]  # To store the Storage instance
        
        # Function to run the storage initialization
        def init_storage_thread():
            try:
                try:
                    # Import storage dependencies inside the thread
                    from pathlib import Path
                    from config.core.storage import get_storage
                    
                    # Try to initialize storage
                    storage = get_storage()
                    storage_instance[0] = storage
                except ModuleNotFoundError as e:
                    # If storage modules are missing, log it but continue
                    print(f"Warning: Storage module missing: {e}")
                except Exception as e:
                    # If storage initialization fails, create a fallback local storage
                    print(f"Warning: Failed to initialize storage: {e}")
                    
                    # Fallback to local storage
                    local_path = Path("tmp/storage")
                    local_path.mkdir(parents=True, exist_ok=True)
                    
                    # Create minimal local storage
                    from lib.core.storage.main import Storage
                    storage_instance[0] = Storage({
                        'driver': 'local',
                        'url_endpoint': str(local_path)
                    })
                
                # Mark initialization as complete
                storage_initialized.set()
            except Exception as e:
                storage_error[0] = e
                storage_initialized.set()
        
        # Start initialization in a thread
        thread = threading.Thread(target=init_storage_thread)
        thread.daemon = True
        thread.start()
        
        # Wait for initialization with timeout
        if not storage_initialized.wait(timeout=timeout_seconds):
            print(f"Warning: Storage initialization timed out after {timeout_seconds} seconds.")
            
            try:
                # Create fallback local storage after timeout
                from pathlib import Path
                from lib.core.storage.main import Storage
                
                local_path = Path("tmp/storage")
                local_path.mkdir(parents=True, exist_ok=True)
                
                storage_instance[0] = Storage({
                    'driver': 'local',
                    'url_endpoint': str(local_path)
                })
                print("Created fallback local storage after timeout.")
            except Exception as fallback_error:
                print(f"Warning: Failed to create fallback storage: {fallback_error}")
            
            return
            
        # Check if we got an error
        if storage_error[0] is not None:
            print(f"Warning: Storage initialization failed: {storage_error[0]}")
        elif storage_instance[0] is not None:
            # Store the storage instance for later use if needed
            self.storage = storage_instance[0]
    
    async def _close_connections(self) -> None:
        """Close all connections."""
        try:
            await close_db()
        except ModuleNotFoundError as e:
            # Module not found is already handled during initialization
            pass
        except Exception as e:
            print(f"Warning: Error closing database connection: {e}")
            
        # Skip Redis disconnection as it's causing event loop issues
        # The Redis connections will be closed automatically when the process exits

def main():
    """Main entry point for the task runner."""
    runner = TaskRunner()
    exit_code = asyncio.run(runner.run())
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
