import inflect
import re

# Initialize inflect engine
p = inflect.engine()

def to_table_name(class_name):
    """
    Convert a class name to a Rails-style table name
    Examples:
    - UserModel => user_models
    - UserModalHash => user_modal_hashes
    - JohnPaulPersonHilda => john_paul_person_hildas
    """
    # Step 1: Convert CamelCase to snake_case
    # First handle the initial uppercase letter
    s = class_name[0].lower() + class_name[1:]
    # Then insert underscores before uppercase letters and convert to lowercase
    s = re.sub(r'([A-Z])', r'_\1', s).lower()
    
    # Step 2: Pluralize the snake_case string
    return p.plural(s)
