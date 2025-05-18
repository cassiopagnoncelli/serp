import os
import sys
import inspect
import importlib
import pkgutil
from typing import Dict, Callable, List, Any, Optional

# Load environment
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.insert(0, project_root)

import lib.core.env

# Dictionary to store registered tasks
_tasks: Dict[str, Callable] = {}
_task_descriptions: Dict[str, str] = {}

def task(description: str = ""):
    """Decorator to register a function as a task."""
    def decorator(func: Callable) -> Callable:
        task_name = func.__name__
        _tasks[task_name] = func
        _task_descriptions[task_name] = description or f"Task: {task_name}"
        return func
    return decorator

def list_tasks() -> List[Dict[str, str]]:
    """List all registered tasks with their descriptions."""
    return [{"name": name, "description": _task_descriptions[name]} for name in sorted(_tasks.keys())]

def run_task(task_name: str, *args, **kwargs) -> Any:
    """Run a registered task by name."""
    if task_name not in _tasks:
        available_tasks = ", ".join(sorted(_tasks.keys()))
        raise ValueError(f"Task '{task_name}' not found. Available tasks: {available_tasks}")
    
    task_func = _tasks[task_name]
    return task_func(*args, **kwargs)

def describe_task(task_name: str) -> Dict[str, Any]:
    """Get description and signature information for a task."""
    if task_name not in _tasks:
        available_tasks = ", ".join(sorted(_tasks.keys()))
        raise ValueError(f"Task '{task_name}' not found. Available tasks: {available_tasks}")
    
    task_func = _tasks[task_name]
    signature = inspect.signature(task_func)
    
    return {
        "name": task_name,
        "description": _task_descriptions[task_name],
        "parameters": [
            {
                "name": param_name,
                "default": str(param.default) if param.default is not inspect.Parameter.empty else None,
                "required": param.default is inspect.Parameter.empty and param.kind != inspect.Parameter.VAR_POSITIONAL and param.kind != inspect.Parameter.VAR_KEYWORD,
                "kind": str(param.kind)
            }
            for param_name, param in signature.parameters.items()
        ]
    }

def load_tasks_from_module(module_path: str) -> int:
    """
    Load tasks from a specified module path.
    Examples:
        - "lib.tasks.maintenance"
        - "lib.tasks.db_migrations"
        
    Returns:
        Number of tasks loaded from the module
    """
    task_count_before = len(_tasks)
    try:
        importlib.import_module(module_path)
        return len(_tasks) - task_count_before
    except ImportError as e:
        print(f"Error loading module {module_path}: {e}")
        return 0

def load_all_tasks() -> int:
    """
    Load all tasks from predefined task directories.
    This function should be called before running any tasks.
    
    Returns:
        Number of tasks loaded
    """
    task_count_before = len(_tasks)
    
    # Default modules to scan for tasks
    default_task_modules = [
        "lib.tasks"
    ]
    
    # Track if we found any modules
    found_modules = False
    
    for module_path in default_task_modules:
        try:
            module = importlib.import_module(module_path)
            found_modules = True
            
            # Try to find submodules if it's a package
            if hasattr(module, "__path__"):
                module_count = 0
                # Use pkgutil instead of importlib.util
                for finder, name, ispkg in pkgutil.iter_modules(module.__path__, f"{module_path}."):
                    try:
                        importlib.import_module(name)
                        module_count += 1
                    except ImportError as e:
                        print(f"Warning: Could not load task module {name}: {e}")
                
                if module_count == 0:
                    print(f"No task modules found in {module_path}")
                    
        except ImportError as e:
            # Skip if module doesn't exist
            print(f"Warning: Could not load tasks from {module_path}: {e}")
    
    if not found_modules:
        print("Warning: No task modules found. You should create modules in lib/tasks/")
    
    return len(_tasks) - task_count_before
