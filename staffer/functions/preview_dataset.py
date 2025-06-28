"""Preview dataset function for Staffer."""

import json
from google.genai import types
from .load_dataset import loaded_datasets


def preview_dataset(working_directory, dataset_name, rows=5):
    """Preview rows from a loaded dataset."""
    try:
        # Validate inputs
        if working_directory is None:
            return json.dumps({"error": "Working directory cannot be None"})
        
        if dataset_name is None:
            return json.dumps({"error": "Dataset name cannot be None"})
        
        # Check if dataset is loaded
        if dataset_name not in loaded_datasets:
            return json.dumps({"error": f"Dataset '{dataset_name}' not loaded. Use load_dataset() first."})
        
        # Get the dataset
        df = loaded_datasets[dataset_name]
        
        # Get sample rows
        sample_df = df.head(rows)
        
        # Prepare result
        result = {
            "dataset_name": dataset_name,
            "sample_size": len(sample_df),
            "total_rows": len(df),
            "columns": list(df.columns),
            "sample_data": sample_df.to_dict('records')
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to get sample: {str(e)}"})


# Schema for Google AI function declaration
schema_preview_dataset = types.FunctionDeclaration(
    name="preview_dataset",
    description="Preview sample rows from a loaded dataset",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the dataset to preview",
            ),
            "rows": types.Schema(
                type=types.Type.NUMBER,
                description="Number of rows to preview (default: 5)",
            ),
        },
        required=["dataset_name"],
    ),
)


# MCP Version Reference:
# async def get_dataset_sample(dataset_name: str, n_rows: int = 5) -> dict:
#     """Sample rows for data preview."""
#     try:
#         df = DatasetManager.get_dataset(dataset_name)
#         
#         # Get sample rows
#         sample_df = df.head(n_rows)
#         
#         return {
#             "dataset_name": dataset_name,
#             "sample_size": len(sample_df),
#             "total_rows": len(df),
#             "columns": list(df.columns),
#             "sample_data": sample_df.to_dict('records')
#         }
#         
#     except Exception as e:
#         return {"error": f"Failed to get sample: {str(e)}"}