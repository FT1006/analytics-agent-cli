"""Main registry that combines all function registries."""

from google.genai import types

# Import all registries
from .file_ops_registry import file_ops_schemas, file_ops_functions
from .excel_registry import excel_schemas, excel_functions
from .analytics_registry import analytics_schemas, analytics_functions

# Combine all schemas
all_schemas = file_ops_schemas + excel_schemas + analytics_schemas

# Combine all function mappings
all_functions = {
    **file_ops_functions,
    **excel_functions,
    **analytics_functions,
}

# Create the combined tool declaration
available_functions = types.Tool(
    function_declarations=all_schemas
)

# Export for use by available_functions.py
__all__ = ['available_functions', 'all_functions']