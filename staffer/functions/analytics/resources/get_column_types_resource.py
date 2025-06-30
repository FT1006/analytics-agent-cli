"""Column types resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional
from google.genai import types


def get_column_types(working_directory: str, dataset_name: Optional[str] = None) -> dict:
    """Column classification (categorical, numerical, temporal, text)."""
    try:
        if dataset_name is None:
            datasets = DatasetManager.list_datasets()
            if not datasets:
                return {"error": "No datasets loaded"}
            dataset_name = datasets[-1]
        
        if dataset_name not in dataset_schemas:
            return {"error": f"Dataset '{dataset_name}' not loaded"}
        
        schema = dataset_schemas[dataset_name]
        
        column_classification = {}
        type_counts = {"numerical": 0, "categorical": 0, "temporal": 0, "identifier": 0}
        
        for col_name, col_info in schema.columns.items():
            column_classification[col_name] = {
                "suggested_role": col_info.suggested_role,
                "dtype": col_info.dtype,
                "unique_values": col_info.unique_values,
                "null_percentage": col_info.null_percentage,
                "sample_values": col_info.sample_values
            }
            type_counts[col_info.suggested_role] += 1
        
        return {
            "dataset_name": dataset_name,
            "column_classification": column_classification,
            "type_summary": type_counts,
            "total_columns": len(schema.columns)
        }
        
    except Exception as e:
        return {"error": f"Failed to get column types: {str(e)}"}


# Gemini function schema
schema_get_column_types = types.FunctionDeclaration(
    name="get_column_types",
    description="Column classification (categorical, numerical, temporal, text)",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the dataset to get column types for (optional - uses most recent if not provided)",
            ),
        },
        required=[],
    ),
)