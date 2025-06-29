"""Get dataset schema function for analytics workflow"""
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from google.genai import types

# Import global storage from load_dataset
from ..tools.load_dataset import loaded_datasets, dataset_schemas


def get_dataset_schema(working_directory, dataset_name):
    """
    Get dynamic schema information for a loaded dataset.
    
    Provides AI with detailed column information, data types, and analysis suggestions
    to enable intelligent analytics decision making.
    
    Args:
        working_directory: The working directory path
        dataset_name (str): Name of the loaded dataset to get schema for
    
    Returns:
        JSON string containing:
            - status (str): "success" or "error"
            - schema (dict): Schema information if successful
            - error (str): Error message if failed
    """
    # Input validation
    if not working_directory:
        return "Error: Working directory cannot be None or empty"
    
    if not dataset_name:
        return "Error: Dataset name cannot be None or empty"
    
    try:
        # Check if schema exists in memory
        if dataset_name in dataset_schemas:
            result = {
                "status": "success",
                "schema": dataset_schemas[dataset_name]
            }
            return json.dumps(result)
        
        # Load schema from persistence if not in memory
        analytics_dir = os.path.join(working_directory, '.staffer_analytics')
        schema_file = os.path.join(analytics_dir, 'schemas', f'{dataset_name}.json')
        
        if os.path.exists(schema_file):
            with open(schema_file, 'r') as f:
                schema = json.load(f)
                dataset_schemas[dataset_name] = schema
                result = {
                    "status": "success", 
                    "schema": schema
                }
                return json.dumps(result)
        
        # Check if dataset is loaded but schema wasn't generated
        if dataset_name in loaded_datasets:
            df = loaded_datasets[dataset_name]
            schema = _generate_schema(df, dataset_name)
            _persist_schema(schema, dataset_name, working_directory)
            dataset_schemas[dataset_name] = schema
            result = {
                "status": "success",
                "schema": schema
            }
            return json.dumps(result)
        
        return f"Error: Dataset '{dataset_name}' not found. Load the dataset first using load_dataset function."
        
    except Exception as e:
        return f"Error: Failed to get dataset schema: {str(e)}"


def _generate_schema(df: pd.DataFrame, dataset_name: str) -> Dict[str, Any]:
    """Generate schema information from DataFrame - reuse existing schema structure"""
    # Use the existing create_dataset_schema function from load_dataset
    from ..tools.load_dataset import create_dataset_schema
    return create_dataset_schema(df, dataset_name)


def _persist_schema(schema: Dict[str, Any], dataset_name: str, working_directory: str) -> None:
    """Persist schema to file system"""
    analytics_dir = os.path.join(working_directory, '.staffer_analytics')
    schemas_dir = os.path.join(analytics_dir, 'schemas')
    os.makedirs(schemas_dir, exist_ok=True)
    
    schema_file = os.path.join(schemas_dir, f'{dataset_name}.json')
    with open(schema_file, 'w') as f:
        json.dump(schema, f, indent=2, default=str)


# Schema for Google AI function declaration
schema_get_dataset_schema = types.FunctionDeclaration(
    name="get_dataset_schema",
    description="Get dynamic schema information for a loaded dataset with column types and analysis suggestions",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the loaded dataset to get schema information for",
            ),
        },
        required=["dataset_name"],
    ),
)


"""
Original MCP Implementation Reference:
=====================================

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional


async def get_dataset_schema(dataset_name: str) -> dict:
    \"\"\"Get dynamic schema for any loaded dataset.\"\"\"
    try:
        if dataset_name not in dataset_schemas:
            return {"error": f"Dataset '{dataset_name}' not loaded"}
        
        schema = dataset_schemas[dataset_name]
        
        # Organize columns by type
        columns_by_type = {
            "numerical": [],
            "categorical": [], 
            "temporal": [],
            "identifier": []
        }
        
        for col_name, col_info in schema.columns.items():
            columns_by_type[col_info.suggested_role].append({
                "name": col_name,
                "dtype": col_info.dtype,
                "unique_values": col_info.unique_values,
                "null_percentage": round(col_info.null_percentage, 1),
                "sample_values": col_info.sample_values
            })
        
        return {
            "dataset_name": dataset_name,
            "total_rows": schema.row_count,
            "total_columns": len(schema.columns),
            "columns_by_type": columns_by_type,
            "suggested_analyses": schema.suggested_analyses,
            "schema_generated": True
        }
        
    except Exception as e:
        return {"error": f"Failed to get schema: {str(e)}"}
"""