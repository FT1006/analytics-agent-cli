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
        "delete_worksheet": delete_worksheet
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
    
    function_result = function_dict[function_name](working_directory, **args)

    return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_name,
            response={"result": function_result},
        )
    ],
)