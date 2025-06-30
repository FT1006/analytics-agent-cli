"""Dataset sample resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional
from google.genai import types


def get_dataset_sample(working_directory: str, dataset_name: str, n_rows: int = 5) -> dict:
    """Sample rows for data preview."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        # Get sample rows
        sample_df = df.head(n_rows)
        
        return {
            "dataset_name": dataset_name,
            "sample_size": len(sample_df),
            "total_rows": len(df),
            "columns": list(df.columns),
            "sample_data": sample_df.to_dict('records')
        }
        
    except Exception as e:
        return {"error": f"Failed to get sample: {str(e)}"}


# Gemini function schema
schema_get_dataset_sample = types.FunctionDeclaration(
    name="get_dataset_sample",
    description="Sample rows for data preview.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the dataset to sample",
            ),
            "n_rows": types.Schema(
                type=types.Type.INTEGER,
                description="Number of rows to sample (default: 5)",
            ),
        },
        required=["dataset_name"],
    ),
)