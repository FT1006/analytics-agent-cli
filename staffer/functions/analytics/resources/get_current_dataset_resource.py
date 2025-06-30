"""Current dataset resource implementation."""

from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from typing import Dict, Any, Optional
from google.genai import types


def get_current_dataset(working_directory: str) -> dict:
    """Currently active dataset name and basic stats."""
    try:
        datasets = DatasetManager.list_datasets()
        
        if not datasets:
            return {
                "status": "no_datasets_loaded",
                "message": "No datasets currently loaded",
                "suggestion": "Use load_dataset() to load a dataset"
            }
        
        # Return info about the most recently loaded dataset
        latest_dataset = datasets[-1]  # Assuming last is most recent
        info = DatasetManager.get_dataset_info(latest_dataset)
        
        return {
            "current_dataset": latest_dataset,
            "shape": info["shape"],
            "memory_mb": round(info["memory_usage_mb"], 2),
            "all_loaded_datasets": datasets,
            "total_datasets": len(datasets)
        }
        
    except Exception as e:
        return {"error": f"Failed to get current dataset: {str(e)}"}


# Gemini function schema
schema_get_current_dataset = types.FunctionDeclaration(
    name="get_current_dataset",
    description="Currently active dataset name and basic stats.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},
        required=[],
    ),
)