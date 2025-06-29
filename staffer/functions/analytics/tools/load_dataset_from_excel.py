"""Load dataset from Excel function that bridges Excel I/O with Analytics workflows.

MCP Reference: No equivalent MCP function exists. The MCP load_dataset_tool only handles 
JSON/CSV files, while this function specifically handles Excel files by bridging the 
Excel I/O layer with the analytics layer. This is unique to Staffer.
"""

import os
import json
import tempfile
import pandas as pd
from google.genai import types

from ...excel.worksheets.read_data_from_excel import read_data_from_excel
from .load_dataset import load_dataset


def load_dataset_from_excel(working_directory, file_path, dataset_name, sheet_name=None):
    """Load Excel data into analytics memory.
    
    This function bridges Excel I/O layer with Analytics layer by:
    1. Reading Excel data using existing read_data_from_excel function
    2. Converting to DataFrame and saving as temporary CSV
    3. Loading into analytics memory using existing load_dataset function
    
    Args:
        working_directory: The permitted working directory
        file_path: Path to Excel file, relative to working directory
        dataset_name: Name to assign to the loaded dataset
        sheet_name: Name of worksheet to read from (defaults to "Sheet1")
        
    Returns:
        JSON string with success/error information
    """
    try:
        # Validate inputs
        if not dataset_name or not dataset_name.strip():
            return "Error: dataset_name cannot be empty"
        
        # Use default sheet name if not provided
        if sheet_name is None:
            sheet_name = "Sheet1"
        
        # Security: Validate file path is within working directory
        working_dir_abs = os.path.abspath(working_directory)
        file_abs_path = os.path.abspath(os.path.join(working_dir_abs, file_path))
        
        if not file_abs_path.startswith(working_dir_abs):
            return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'
        
        # Step 1: Read Excel data using existing function
        excel_result_str = read_data_from_excel(working_directory, file_path, sheet_name)
        
        # Check if read_data_from_excel returned an error
        if excel_result_str.startswith("Error:"):
            return excel_result_str
        
        # Parse the Excel data result
        try:
            excel_result = json.loads(excel_result_str)
        except json.JSONDecodeError:
            return f"Error: Invalid response from Excel reader: {excel_result_str}"
        
        # Step 2: Convert Excel data to DataFrame
        data = excel_result.get('data', [])
        if not data:
            return "Error: No data found in Excel sheet"
        
        # Validate data structure
        if len(data) < 1:
            return "Error: Excel sheet is empty"
        
        headers = data[0]
        rows = data[1:] if len(data) > 1 else []
        
        # Validate headers
        if not headers or all(h is None for h in headers):
            return "Error: Excel sheet has no valid column headers"
        
        # Create DataFrame
        df = pd.DataFrame(rows, columns=headers)
        
        # Step 3: Save DataFrame as temporary CSV with better name collision handling
        temp_csv_filename = f'.temp_{dataset_name}_{os.getpid()}.csv'
        temp_csv_path = os.path.join(working_directory, temp_csv_filename)
        
        try:
            df.to_csv(temp_csv_path, index=False)
            
            # Step 4: Load into analytics memory using existing load_dataset
            load_result_str = load_dataset(working_directory, temp_csv_filename, dataset_name)
            
            # Check if load_dataset returned an error
            if load_result_str.startswith("Error:"):
                return load_result_str
            
            # Parse load_dataset result and enhance with Excel-specific info
            try:
                load_result = json.loads(load_result_str)
            except json.JSONDecodeError:
                return f"Error: Invalid response from dataset loader: {load_result_str}"
            
            # Create enhanced result with Excel-specific information
            result = {
                "status": "loaded",
                "dataset_name": dataset_name,
                "source_file": file_path,
                "sheet_name": sheet_name,
                "rows": load_result.get('rows', len(df)),
                "columns": load_result.get('columns', list(df.columns)),
                "format": "excel"
            }
            
            return json.dumps(result, indent=2)
            
        finally:
            # Always clean up temporary CSV file
            if os.path.exists(temp_csv_path):
                try:
                    os.remove(temp_csv_path)
                except OSError:
                    pass  # Ignore cleanup errors
        
    except Exception as e:
        return f"Error: Failed to load dataset from Excel: {str(e)}"


# Schema for Google AI function declaration
schema_load_dataset_from_excel = types.FunctionDeclaration(
    name="load_dataset_from_excel",
    description="Load Excel data into analytics memory for analysis workflows",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to Excel file, relative to the working directory",
            ),
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name to assign to the loaded dataset for future reference",
            ),
            "sheet_name": types.Schema(
                type=types.Type.STRING,
                description="Name of worksheet to read from (optional, defaults to 'Sheet1')",
            ),
        },
        required=["file_path", "dataset_name"],
    ),
)