from google.genai import types
import traceback

from .functions.get_files_info import schema_get_files_info, get_files_info
from .functions.get_file_content import schema_get_file_content, get_file_content
from .functions.write_file import schema_write_file, write_file
from .functions.run_python_file import schema_run_python_file, run_python_file
from .functions.get_working_directory import schema_get_working_directory, get_working_directory
from .functions.create_workbook import schema_create_workbook, create_workbook
from .functions.create_worksheet import schema_create_worksheet, create_worksheet
from .functions.get_workbook_metadata import schema_get_workbook_metadata, get_workbook_metadata
from .functions.rename_worksheet import schema_rename_worksheet, rename_worksheet
from .functions.delete_worksheet import schema_delete_worksheet, delete_worksheet
from .functions.read_data_from_excel import schema_read_data_from_excel, read_data_from_excel
from .functions.write_data_to_excel import schema_write_data_to_excel, write_data_to_excel
from .functions.copy_worksheet import schema_copy_worksheet, copy_worksheet
from .functions.validate_excel_range import schema_validate_excel_range, validate_excel_range
from .functions.merge_cells import schema_merge_cells, merge_cells
from .functions.unmerge_cells import schema_unmerge_cells, unmerge_cells
from .functions.copy_range import schema_copy_range, copy_range
from .functions.delete_range import schema_delete_range, delete_range
from .functions.validate_formula_syntax import schema_validate_formula_syntax, validate_formula_syntax
from .functions.apply_formula import schema_apply_formula, apply_formula
from .functions.get_data_validation_info import schema_get_data_validation_info, get_data_validation_info
from .functions.format_range import schema_format_range, format_range
from .functions.create_table import schema_create_table, create_table
from .functions.create_chart import schema_create_chart, create_chart
from .functions.create_pivot_table import schema_create_pivot_table, create_pivot_table
from .functions.load_dataset import schema_load_dataset, load_dataset
from .functions.list_loaded_datasets import schema_list_loaded_datasets, list_loaded_datasets
from .functions.load_dataset_from_excel import schema_load_dataset_from_excel, load_dataset_from_excel
from .functions.export_analysis_to_excel import schema_export_analysis_to_excel, export_analysis_to_excel


available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
        schema_get_working_directory,
        schema_create_workbook,
        schema_create_worksheet,
        schema_get_workbook_metadata,
        schema_rename_worksheet,
        schema_delete_worksheet,
        schema_read_data_from_excel,
        schema_write_data_to_excel,
        schema_copy_worksheet,
        schema_validate_excel_range,
        schema_merge_cells,
        schema_unmerge_cells,
        schema_copy_range,
        schema_delete_range,
        schema_validate_formula_syntax,
        schema_apply_formula,
        schema_get_data_validation_info,
        schema_format_range,
        schema_create_table,
        schema_create_chart,
        schema_create_pivot_table,
        schema_load_dataset,
        schema_list_loaded_datasets,
        schema_load_dataset_from_excel,
        schema_export_analysis_to_excel,
    ]
)

def get_available_functions(working_dir):
    return available_functions

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
    
    # Keep original args but we'll add error handling
    function_dict = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "write_file": write_file,
        "run_python_file": run_python_file,
        "get_working_directory": get_working_directory,
        "create_workbook": create_workbook,
        "create_worksheet": create_worksheet,
        "get_workbook_metadata": get_workbook_metadata,
        "rename_worksheet": rename_worksheet,
        "delete_worksheet": delete_worksheet,
        "read_data_from_excel": read_data_from_excel,
        "write_data_to_excel": write_data_to_excel,
        "copy_worksheet": copy_worksheet,
        "validate_excel_range": validate_excel_range,
        "merge_cells": merge_cells,
        "unmerge_cells": unmerge_cells,
        "copy_range": copy_range,
        "delete_range": delete_range,
        "validate_formula_syntax": validate_formula_syntax,
        "apply_formula": apply_formula,
        "get_data_validation_info": get_data_validation_info,
        "format_range": format_range,
        "create_table": create_table,
        "create_chart": create_chart,
        "create_pivot_table": create_pivot_table,
        "load_dataset": load_dataset,
        "list_loaded_datasets": list_loaded_datasets,
        "load_dataset_from_excel": load_dataset_from_excel,
        "export_analysis_to_excel": export_analysis_to_excel
    }

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