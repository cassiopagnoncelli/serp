import os
import sys
import platform
from typing import Dict, Any, List
import datetime

from lib.core.task import task
from lib.core.dt import DateTime

@task("Print system information")
def system_info() -> Dict[str, Any]:
    """
    Print information about the system.
    
    Returns:
        A dictionary with system information.
    """
    return {
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "current_time": DateTime.utc().isoformat(),
        "system": platform.system(),
        "node": platform.node(),
        "release": platform.release(),
        "version": platform.version(),
        "processor": platform.processor(),
        "architecture": platform.architecture()[0],
        "cpu_count": os.cpu_count()
    }

@task("Calculate factorial")
def factorial(n: int = 10) -> Dict[str, Any]:
    """
    Calculate the factorial of a number.
    
    Args:
        n: The number to calculate factorial for.
        
    Returns:
        A dictionary with the result and calculation time.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers")
    
    start_time = DateTime.utc()
    
    result = 1
    for i in range(1, n + 1):
        result *= i
    
    end_time = DateTime.utc()
    elapsed = (end_time - start_time).total_seconds()
    
    return {
        "input": n,
        "result": result,
        "calculation_time": elapsed,
        "timestamp": DateTime.utc().isoformat()
    }

@task("List environment variables")
def env_vars(filter_prefix: str = None) -> Dict[str, Any]:
    """
    List environment variables, optionally filtered by prefix.
    
    Args:
        filter_prefix: Only include variables that start with this prefix.
        
    Returns:
        A dictionary with environment variables.
    """
    env_dict = dict(os.environ)
    
    # Filter variables if a prefix is provided
    if filter_prefix:
        env_dict = {k: v for k, v in env_dict.items() if k.startswith(filter_prefix)}
    
    # Sort the environment variables
    sorted_env = dict(sorted(env_dict.items()))
    
    return {
        "variables": sorted_env,
        "count": len(sorted_env),
        "filter_prefix": filter_prefix,
        "timestamp": DateTime.utc().isoformat()
    }
