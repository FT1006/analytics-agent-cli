"""Load dataset analytic function for Staffer."""

import os
import json
import pandas as pd
from google.genai import types
from datetime import datetime


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
        
        # Create and save schema
        schema = create_dataset_schema(df, dataset_name)
        schema_file = os.path.join(schemas_dir, f'{dataset_name}.json')
        with open(schema_file, 'w') as f:
            json.dump(schema, f, indent=2)
        
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