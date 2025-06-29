"""Load dataset analytic function for Staffer."""

import os
import json
import pandas as pd
from google.genai import types
from datetime import datetime
from typing import Dict

# Global in-memory storage for datasets (Stage 2 optimization)
loaded_datasets: Dict[str, pd.DataFrame] = {}
dataset_schemas: Dict[str, dict] = {}


def load_dataset(working_directory, file_path, dataset_name):
    """Load any JSON/CSV dataset with automatic schema discovery and file-based persistence."""
    try:
        # Security: Validate file path is within working directory
        working_dir_abs = os.path.abspath(working_directory)
        file_abs_path = os.path.abspath(os.path.join(working_dir_abs, file_path))
        
        if not file_abs_path.startswith(working_dir_abs):
            return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'
        
        # Check if file exists
        if not os.path.exists(file_abs_path):
            return f'Error: File "{file_path}" not found'
        
        # Determine format from file extension
        if file_path.endswith('.json'):
            df = pd.read_json(file_abs_path)
            file_format = 'json'
        elif file_path.endswith('.csv'):
            df = pd.read_csv(file_abs_path)
            file_format = 'csv'
        else:
            return f'Error: Unsupported file format: {file_path}. Only CSV and JSON are supported.'
        
        # Create analytics directory structure
        analytics_dir = os.path.join(working_directory, '.staffer_analytics')
        datasets_dir = os.path.join(analytics_dir, 'datasets')
        schemas_dir = os.path.join(analytics_dir, 'schemas')
        
        os.makedirs(datasets_dir, exist_ok=True)
        os.makedirs(schemas_dir, exist_ok=True)
        
        # Save dataset to analytics directory
        dataset_file = os.path.join(datasets_dir, f'{dataset_name}.csv')
        df.to_csv(dataset_file, index=False)
        
        # Store in memory for performance (Stage 2 optimization)
        loaded_datasets[dataset_name] = df
        
        # Create and save schema
        schema = create_dataset_schema(df, dataset_name)
        dataset_schemas[dataset_name] = schema
        schema_file = os.path.join(schemas_dir, f'{dataset_name}.json')
        with open(schema_file, 'w') as f:
            json.dump(schema, f, indent=2)
        
        # Save lightweight registry entry for cross-session persistence
        save_registry_entry(working_directory, dataset_name, file_path)
        
        # Return success result as JSON string
        result = {
            "status": "loaded",
            "dataset_name": dataset_name,
            "rows": len(df),
            "columns": list(df.columns),
            "format": file_format,
            "memory_usage": f"{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB"
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return f"Error: Failed to load dataset: {str(e)}"


def create_dataset_schema(df, dataset_name):
    """Create schema information for a dataset."""
    columns = {}
    
    for col in df.columns:
        series = df[col]
        
        # Determine suggested role
        if pd.api.types.is_numeric_dtype(series):
            role = 'numerical'
        elif pd.api.types.is_datetime64_any_dtype(series):
            role = 'temporal'
        elif series.nunique() / len(series) < 0.5:  # Low cardinality = categorical
            role = 'categorical'
        elif series.nunique() == len(series):  # Unique values = identifier
            role = 'identifier'
        else:
            role = 'categorical'
        
        columns[col] = {
            'name': col,
            'dtype': str(series.dtype),
            'unique_values': int(series.nunique()),
            'null_percentage': float(series.isnull().mean() * 100),
            'sample_values': series.dropna().head(3).tolist(),
            'suggested_role': role
        }
    
    # Generate analysis suggestions based on column types
    suggestions = []
    numerical_cols = [col for col, info in columns.items() if info['suggested_role'] == 'numerical']
    categorical_cols = [col for col, info in columns.items() if info['suggested_role'] == 'categorical']
    temporal_cols = [col for col, info in columns.items() if info['suggested_role'] == 'temporal']
    
    if len(numerical_cols) >= 2:
        suggestions.append("correlation_analysis")
    if categorical_cols:
        suggestions.append("segmentation_analysis")
    if temporal_cols:
        suggestions.append("time_series_analysis")
    
    return {
        'name': dataset_name,
        'columns': columns,
        'row_count': len(df),
        'suggested_analyses': suggestions
    }


def get_dataset(working_directory, dataset_name):
    """Retrieve dataset from memory with fallback to reload from file."""
    # First try memory
    if dataset_name in loaded_datasets:
        return loaded_datasets[dataset_name]
    
    # Fallback: Check registry and reload
    analytics_dir = os.path.join(working_directory, '.staffer_analytics')
    registry_file = os.path.join(analytics_dir, 'registry.json')
    
    if os.path.exists(registry_file):
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        if dataset_name in registry:
            # Reload from file
            dataset_file = os.path.join(analytics_dir, 'datasets', f'{dataset_name}.csv')
            if os.path.exists(dataset_file):
                df = pd.read_csv(dataset_file)
                loaded_datasets[dataset_name] = df
                
                # Reload schema too
                schema_file = os.path.join(analytics_dir, 'schemas', f'{dataset_name}.json')
                if os.path.exists(schema_file):
                    with open(schema_file, 'r') as f:
                        dataset_schemas[dataset_name] = json.load(f)
                
                return df
    
    # Dataset not found
    raise ValueError(f"Dataset '{dataset_name}' not loaded. Use load_dataset() first.")


def save_registry_entry(working_directory, dataset_name, file_path):
    """Save lightweight registry entry for cross-session persistence."""
    analytics_dir = os.path.join(working_directory, '.staffer_analytics')
    registry_file = os.path.join(analytics_dir, 'registry.json')
    
    # Load existing registry or create new
    if os.path.exists(registry_file):
        with open(registry_file, 'r') as f:
            registry = json.load(f)
    else:
        registry = {}
    
    # Add/update entry
    registry[dataset_name] = {
        'file_path': file_path,
        'loaded_at': datetime.now().isoformat()
    }
    
    # Save registry
    with open(registry_file, 'w') as f:
        json.dump(registry, f, indent=2)


# Schema for Google AI function declaration
schema_load_dataset = types.FunctionDeclaration(
    name="load_dataset",
    description="Load any JSON/CSV dataset with automatic schema discovery and persistence",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the dataset file (CSV or JSON) relative to working directory",
            ),
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name to assign to the loaded dataset for future reference",
            ),
        },
        required=["file_path", "dataset_name"],
    ),
)

# MCP version (from /Users/spaceship/project/analytic-agent-cli/function_bank/mcp_server/tools/load_dataset_tool.py):
# """Dataset loading tool implementation."""
#
#  import pandas as pd
# import numpy as np
# from typing import List, Dict, Any, Optional, Union
# from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig
#
#
# async def load_dataset(file_path: str, dataset_name: str, sample_size: Optional[int] = None) -> dict:
#     """Load any JSON/CSV dataset into memory with automatic schema discovery."""
#     try:
#         result = DatasetManager.load_dataset(file_path, dataset_name)
#     
#         # Apply sampling if requested
#         if sample_size and sample_size < result["rows"]:
#             df = DatasetManager.get_dataset(dataset_name)
#             sampled_df = df.sample(n=sample_size, random_state=42)
#             loaded_datasets[dataset_name] = sampled_df
#
#             # Update schema for sampled data
#             schema = dataset_schemas[dataset_name]
#             schema.row_count = len(sampled_df)
#         
#             result["rows"] = len(sampled_df)
#             result["sampled"] = True
#             result["original_rows"] = len(df)
#
#         return result
#
#     except Exception as e:
#         return {
#             "status": "error",
#             "message": f"Failed to load dataset: {str(e)}"
#         }