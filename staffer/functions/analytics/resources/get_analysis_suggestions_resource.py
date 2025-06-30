"""Analysis suggestions resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional
from google.genai import types


def get_analysis_suggestions(working_directory: str, dataset_name: Optional[str] = None) -> dict:
    """AI-generated analysis recommendations."""
    try:
        if dataset_name is None:
            datasets = DatasetManager.list_datasets()
            if not datasets:
                return {"error": "No datasets loaded"}
            dataset_name = datasets[-1]
        
        # Import here to avoid circular imports
        from ..tools.pandas_tools import suggest_analysis
        return suggest_analysis(working_directory, dataset_name)
        
    except Exception as e:
        return {"error": f"Failed to get suggestions: {str(e)}"}


# Gemini function schema
schema_get_analysis_suggestions = types.FunctionDeclaration(
    name="get_analysis_suggestions",
    description="AI-generated analysis recommendations",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the dataset to get suggestions for (optional - uses most recent if not provided)",
            ),
        },
        required=[],
    ),
)