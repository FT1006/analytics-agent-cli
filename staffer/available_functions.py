from google.genai import types

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
    ]
)

def get_available_functions(working_dir):
    return available_functions

def call_function(function_call_part, working_directory, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    args = function_call_part.args or {}
    function_name = function_call_part.name.lower()
    
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
        "create_pivot_table": create_pivot_table
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
    except AttributeError as e:
        # Catch 'NoneType' object has no attribute errors
        if "'NoneType' object has no attribute" in str(e):
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"result": f"Error: One or more required parameters are None. {str(e)}"},
                    )
                ],
            )
        else:
            # Re-raise other AttributeErrors
            raise
    except TypeError as e:
        # Catch 'NoneType' object is not iterable errors
        if "NoneType" in str(e):
            return types.Content(
                role="tool", 
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"result": f"Error: Invalid None value passed to function. {str(e)}"},
                    )
                ],
            )
        else:
            # Re-raise other TypeErrors
            raise

    return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_name,
            response={"result": function_result},
        )
    ],
)