"""Main entry point for available functions in Staffer."""

from google.genai import types
import traceback

# Import the combined registry from the subfolder
from .function_registries import available_functions as tool_registry, all_functions as function_dict


def get_available_functions(working_dir):
    """Get all available functions for the given working directory."""
    return tool_registry


def _create_args_summary(args):
    """Create a concise summary of arguments for logging."""
    if args is None:
        return " (no args)"
    
    if not args:
        return " (empty args: {})"
    
    # Create summary showing arg names and values
    summary_parts = []
    for key, value in args.items():
        if value is None:
            summary_parts.append(f"{key}=None")
        elif isinstance(value, str) and not value.strip():
            summary_parts.append(f"{key}=''")
        elif isinstance(value, str) and len(value) > 20:
            summary_parts.append(f"{key}='{value[:15]}...'")
        else:
            summary_parts.append(f"{key}={repr(value)}")
    
    return f" ({', '.join(summary_parts)})"


def _create_result_summary(result):
    """Create a concise summary of the function result."""
    if result is None:
        return "None"
    
    result_str = str(result)
    
    # Handle different result types
    if isinstance(result, dict):
        # For JSON-like results, show key info
        if 'status' in result:
            return f"status={result['status']}"
        elif 'error' in result:
            return f"error={result['error']}"
        else:
            return f"dict with {len(result)} keys"
    
    # Handle error messages
    if result_str.startswith("Error:"):
        # Truncate long error messages
        if len(result_str) > 50:
            return result_str[:47] + "..."
        return result_str
    
    # Handle success messages
    if len(result_str) > 60:
        return result_str[:57] + "..."
    
    return result_str


def call_function(function_call_part, working_directory, verbose=False):
    """Call a function with the given arguments and working directory."""
    args = function_call_part.args or {}
    function_name = function_call_part.name.lower()
    
    # Enhanced function call visibility
    if verbose:
        print(f"🔍 DETAILED FUNCTION CALL ANALYSIS:")
        print(f"   Function: {function_call_part.name}")
        print(f"   Raw args from LLM: {function_call_part.args}")
        print(f"   Processed args: {args}")
        print(f"   Args type: {type(function_call_part.args)}")
        if args:
            for key, value in args.items():
                print(f"   - {key}: {repr(value)} (type: {type(value).__name__})")
    else:
        # Enhanced basic mode with parameter visibility
        args_summary = _create_args_summary(function_call_part.args)
        print(f" - Calling function: {function_name}{args_summary}")
    
    if function_name not in function_dict:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )
    
    try:
        function_result = function_dict[function_name](working_directory, **args)
        
        # Display function result based on verbosity
        if verbose:
            print(f"   Result: {repr(function_result)}")
            print(f"   Result type: {type(function_result).__name__}")
        else:
            # Create a summary of the result for basic mode
            result_summary = _create_result_summary(function_result)
            print(f"   → Result: {result_summary}")
        
        # Return successful result
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )
            
    except AttributeError as e:
        # Catch 'NoneType' object has no attribute errors
        if "'NoneType' object has no attribute" in str(e):
            error_msg = f"Error: One or more required parameters are None. {str(e)}"
            if verbose:
                print(f"   ❌ Error: {error_msg}")
                print(f"   ❌ Full traceback: {traceback.format_exc()}")
            else:
                print(f"   → Error: None parameter")
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"result": error_msg},
                    )
                ],
            )
        else:
            # Re-raise other AttributeErrors for general handler
            raise
    except TypeError as e:
        # Catch 'NoneType' object is not iterable errors
        if "NoneType" in str(e):
            error_msg = f"Error: Invalid None value passed to function. {str(e)}"
            if verbose:
                print(f"   ❌ Error: {error_msg}")
                print(f"   ❌ Full traceback: {traceback.format_exc()}")
            else:
                print(f"   → Error: None value")
            return types.Content(
                role="tool", 
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"result": error_msg},
                    )
                ],
            )
        else:
            # Re-raise other TypeErrors for general handler
            raise
    except Exception as e:
        # Catch all other exceptions with full debugging info
        error_msg = f"Error: Function {function_name} failed: {str(e)}"
        if verbose:
            print(f"   ❌ Error: {error_msg}")
            print(f"   ❌ Exception type: {type(e).__name__}")
            print(f"   ❌ Full traceback: {traceback.format_exc()}")
        else:
            print(f"   → Error: {str(e)}")
        
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": error_msg},
                )
            ],
        )