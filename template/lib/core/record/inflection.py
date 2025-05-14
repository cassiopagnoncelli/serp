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

def to_class_name(table_name):
    """
    Convert a Rails-style table name to a class name
    Examples:
    - user_models => UserModel
    - user_modal_hashes => UserModalHash
    - john_paul_person_hildas => JohnPaulPersonHilda
    """
    # Step 1: Singularize the table name
    singular = p.singular_noun(table_name)
    if not singular:  # If already singular
        singular = table_name
    
    # Step 2: Convert snake_case to CamelCase
    # Split by underscore and capitalize each word
    words = singular.split('_')
    # Capitalize first letter of each word and join
    return ''.join(word.capitalize() for word in words)

