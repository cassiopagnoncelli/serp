"""
Example tasks to demonstrate the task system.

These tasks show different patterns for defining tasks with various parameter types.
"""

from typing import Dict, Any, List, Optional
import time
import random

from lib.core.task import task

@task("Simple task with no parameters")
def hello_world() -> str:
    """
    A simple task that returns a greeting.
    
    Returns:
        A greeting message
    """
    return "Hello, World!"

@task("Task with required and optional parameters")
def greeting(name: str, title: str = "User") -> str:
    """
    Greet someone with their name and optional title.
    
    Args:
        name: The name of the person to greet
        title: An optional title (default: "User")
        
    Returns:
        A personalized greeting
    """
    return f"Hello, {title} {name}!"

@task("Task with multiple return values")
def generate_numbers(count: int = 5, min_val: int = 1, max_val: int = 100) -> Dict[str, Any]:
    """
    Generate random numbers and statistics.
    
    Args:
        count: Number of random numbers to generate
        min_val: Minimum value for random numbers
        max_val: Maximum value for random numbers
        
    Returns:
        A dictionary with the generated numbers and statistics
    """
    numbers = [random.randint(min_val, max_val) for _ in range(count)]
    
    return {
        "numbers": numbers,
        "count": len(numbers),
        "min": min(numbers),
        "max": max(numbers),
        "average": sum(numbers) / len(numbers),
        "sum": sum(numbers)
    }

@task("Task with error handling")
def divide(a: float, b: float) -> Dict[str, Any]:
    """
    Divide two numbers with error handling.
    
    Args:
        a: The numerator
        b: The denominator
        
    Returns:
        A dictionary with the result and operation details
        
    Raises:
        ValueError: If the denominator is zero
    """
    if b == 0:
        raise ValueError("Cannot divide by zero")
    
    result = a / b
    
    return {
        "operation": f"{a} / {b}",
        "result": result,
        "inputs": {
            "a": a,
            "b": b
        }
    }

@task("Long-running task with progress")
def long_operation(iterations: int = 5, sleep_time: float = 1.0) -> Dict[str, Any]:
    """
    Simulate a long-running operation with progress updates.
    
    Args:
        iterations: Number of iterations to perform
        sleep_time: Time to sleep between iterations (seconds)
        
    Returns:
        A dictionary with operation results
    """
    start_time = time.time()
    
    for i in range(iterations):
        # Print progress (will be visible in the console)
        progress = (i + 1) / iterations * 100
        print(f"Progress: {progress:.1f}% (step {i+1}/{iterations})")
        
        # Simulate work
        time.sleep(sleep_time)
    
    end_time = time.time()
    elapsed = end_time - start_time
    
    return {
        "iterations": iterations,
        "sleep_time": sleep_time,
        "total_time": elapsed,
        "average_time_per_iteration": elapsed / iterations,
        "completed": True
    }

@task("Task with list parameters")
def process_items(items: List[str], prefix: str = "", suffix: str = "") -> Dict[str, Any]:
    """
    Process a list of items by adding prefixes and suffixes.
    
    Args:
        items: List of strings to process
        prefix: Prefix to add to each item
        suffix: Suffix to add to each item
        
    Returns:
        A dictionary with processed items
    """
    processed = [f"{prefix}{item}{suffix}" for item in items]
    
    return {
        "original": items,
        "processed": processed,
        "count": len(items),
        "prefix": prefix,
        "suffix": suffix
    }
