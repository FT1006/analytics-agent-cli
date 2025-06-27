"""Create Excel workbook function."""

import os
from pathlib import Path
from google.genai import types

try:
    from openpyxl import Workbook
    OPENPYXL_AVAILABLE = True
except ImportError:
    OPENPYXL_AVAILABLE = False


def create_workbook(working_directory, filepath):
    """Create new Excel workbook.
    
    Args:
        working_directory: The permitted working directory
        filepath: Path to create workbook, relative to working directory
        
    Returns:
        String result message
    """
    if not OPENPYXL_AVAILABLE:
        return "Error: openpyxl library not available. Please install with: pip install openpyxl"
    
    # Security: Validate file path is within working directory
    working_dir_abs = os.path.abspath(working_directory)
    file_abs_path = os.path.abspath(os.path.join(working_dir_abs, filepath))
    
    if not file_abs_path.startswith(working_dir_abs):
        return f'Error: Cannot create "{filepath}" as it is outside the permitted working directory'
    
    try:
        # Create workbook using openpyxl
        wb = Workbook()
        
        # Ensure directory exists
        Path(file_abs_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Save workbook
        wb.save(file_abs_path)
        
        return f"Created workbook at {filepath}"
        
    except Exception as e:
        return f"Error: {str(e)}"


# Schema for Google AI function declaration
schema_create_workbook = types.FunctionDeclaration(
    name="create_workbook",
    description="Create a new Excel workbook file",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "filepath": types.Schema(
                type=types.Type.STRING,
                description="Path to create the workbook file, relative to the working directory",
            ),
        },
        required=["filepath"],
    ),
)