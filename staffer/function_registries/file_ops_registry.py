"""File operations function registry for Staffer."""

from google.genai import types

# Import file operations functions and schemas
from ..functions.file_ops.get_files_info import schema_get_files_info, get_files_info
from ..functions.file_ops.get_file_content import schema_get_file_content, get_file_content
from ..functions.file_ops.write_file import schema_write_file, write_file
from ..functions.file_ops.run_python_file import schema_run_python_file, run_python_file
from ..functions.file_ops.get_working_directory import schema_get_working_directory, get_working_directory

# File operations schemas list
file_ops_schemas = [
    schema_get_files_info,
    schema_get_file_content,
    schema_write_file,
    schema_run_python_file,
    schema_get_working_directory,
]

# File operations function mapping
file_ops_functions = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
    "get_working_directory": get_working_directory,
}