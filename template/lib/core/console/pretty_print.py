import colorama
from colorama import Fore, Style
from typing import Any, Dict, List
from tortoise.models import Model
import json
from enum import Enum, EnumType
import asyncio

colorama.init()

class PrettyPrinter:
    @staticmethod
    def format_value(value: Any) -> str:
        """Format a value based on its type."""
        if value is None:
            return f"{Fore.RED}{Style.BRIGHT}nil{Style.RESET_ALL}"
        elif type(value).__class__ == EnumType:
            return f"{Fore.CYAN}{Style.BRIGHT}{value.value}{Style.RESET_ALL}"
        elif isinstance(value, dict):
            # For dictionaries, indent each line by 3 spaces
            json_str = json.dumps(value, indent=2)
            indented_json = '\n'.join('   ' + line for line in json_str.split('\n'))
            return f"{Fore.GREEN}{indented_json}{Style.RESET_ALL}"
        elif isinstance(value, (list, tuple)):
            return f"{Fore.MAGENTA}{value}{Style.RESET_ALL}"
        elif isinstance(value, str):
            return f"{Fore.YELLOW}'{value}'{Style.RESET_ALL}"
        elif isinstance(value, bool):
            color = Fore.GREEN if value else Fore.RED
            return f"{color}{Style.BRIGHT}{value}{Style.RESET_ALL}"
        elif isinstance(value, (int, float)):
            return f"{Fore.CYAN}{Style.BRIGHT}{value}{Style.RESET_ALL}"
        else:
            return f"{Fore.MAGENTA}{value}{Style.RESET_ALL}"

    @staticmethod
    def print_model(model: Model) -> None:
        """Pretty print a Tortoise ORM model in Rails console style."""
        # Get model data
        model_dict = model.to_dict()
        model_name = type(model).__name__
        
        # Print model header
        print(f"{Fore.GREEN}{model_name} {{ {Style.RESET_ALL}")
        
        # Calculate max key length for alignment
        max_key_length = max(len(str(k)) for k in model_dict.keys())
        
        # Print each attribute with 3-space indentation
        for key, value in model_dict.items():
            key_str = str(key).ljust(max_key_length)
            value_str = PrettyPrinter.format_value(value)
            print(f"   {Fore.WHITE}{key_str} {Style.RESET_ALL}: {value_str}")
        
        print(f"{Fore.GREEN}}} {Style.RESET_ALL}")
    
    @staticmethod
    def print_models(models: List[Model]) -> None:
        """Pretty print a list of Tortoise ORM models."""
        for model in models:
            PrettyPrinter.print_model(model)

# Add a helper function to the global namespace
def pp(obj: Any) -> None:
    """Pretty print an object or a list of objects."""
    if isinstance(obj, list) and all(isinstance(item, Model) for item in obj):
        PrettyPrinter.print_models(obj)
    elif isinstance(obj, Model):
        PrettyPrinter.print_model(obj)
    elif isinstance(obj, list) and all(isinstance(item, dict) for item in obj):
        # Handle list of dictionaries
        for item in obj:
            # For dictionaries, indent each line by 3 spaces
            json_str = json.dumps(item, indent=2, default=str)  # Added default=str to handle datetime
            indented_json = '\n'.join('   ' + line for line in json_str.split('\n'))
            print(f"{Fore.GREEN}{indented_json}{Style.RESET_ALL}")
            print()  # Add blank line between items
    elif isinstance(obj, dict):
        # For plain dictionaries, also use 3-space indentation
        json_str = json.dumps(obj, indent=2, default=str)  # Added default=str to handle datetime
        indented_json = '\n'.join('   ' + line for line in json_str.split('\n'))
        print(f"{Fore.GREEN}{indented_json}{Style.RESET_ALL}")
    else:
        print(obj) 