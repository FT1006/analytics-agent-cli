"""Validation utilities for function inputs."""

from functools import wraps
from typing import Any, Callable, Dict, Optional
import inspect


def validate_inputs(validation_rules: Optional[Dict[str, Callable]] = None):
    """Decorator to validate function inputs before execution.
    
    Args:
        validation_rules: Dict mapping parameter names to validation functions.
                         If None, applies default None checks to all string parameters.
    
    Example:
        @validate_inputs({
            'data_range': lambda x: x and ':' in x,
            'sheet_name': lambda x: x and x.strip()
        })
        def my_function(data_range: str, sheet_name: str):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get function signature
            sig = inspect.signature(func)
            bound_args = sig.bind(*args, **kwargs)
            bound_args.apply_defaults()
            
            # Apply validation
            for param_name, param_value in bound_args.arguments.items():
                # Skip working_directory parameter (always first)
                if param_name == 'working_directory':
                    continue
                    
                # Apply custom validation if provided
                if validation_rules and param_name in validation_rules:
                    validator = validation_rules[param_name]
                    if not validator(param_value):
                        return f"Error: Invalid {param_name}: {param_value}"
                        
                # Default validation for string parameters
                elif param_value is None:
                    # Check if this parameter has a default value
                    param = sig.parameters.get(param_name)
                    if param and param.default is inspect.Parameter.empty:
                        # Required parameter is None
                        return f"Error: {param_name} cannot be None"
                        
            return func(*args, **kwargs)
        return wrapper
    return decorator


def validate_cell_range(range_str: Optional[str]) -> bool:
    """Validate cell range format like 'A1:B10'."""
    if not range_str:
        return False
    return ':' in range_str or _is_valid_cell_reference(range_str)


def _is_valid_cell_reference(cell_ref: str) -> bool:
    """Check if string is a valid cell reference like 'A1'."""
    if not cell_ref or len(cell_ref) < 2:
        return False
    
    # Split into column letters and row numbers
    col_part = []
    row_part = []
    
    for char in cell_ref:
        if char.isalpha():
            if row_part:  # Letters after numbers is invalid
                return False
            col_part.append(char)
        elif char.isdigit():
            row_part.append(char)
        else:
            return False
    
    return len(col_part) > 0 and len(row_part) > 0


def ensure_not_none(value: Any, param_name: str) -> Any:
    """Ensure value is not None, raise descriptive error if it is."""
    if value is None:
        raise ValueError(f"{param_name} cannot be None")
    return value


def ensure_string_not_empty(value: Optional[str], param_name: str) -> str:
    """Ensure string value is not None or empty."""
    if not value:
        raise ValueError(f"{param_name} cannot be None or empty")
    return value