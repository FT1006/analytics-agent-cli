"""List loaded datasets analytic function for Staffer."""

import os
import json
from datetime import datetime
from google.genai import types

from ..tools.load_dataset import loaded_datasets, get_dataset


def list_loaded_datasets(working_directory):
    """List all loaded datasets with their metadata including rows, columns, and memory usage."""
    try:
        # Security: Validate working directory
        if not working_directory:
            return "Error: Working directory cannot be None or empty"
        
        working_dir_abs = os.path.abspath(working_directory)
        if not os.path.exists(working_dir_abs):
            return f"Error: Working directory '{working_directory}' does not exist"
        
        datasets_info = []
        registry = {}
        
        # Load registry to get loaded_at timestamps
        analytics_dir = os.path.join(working_directory, '.staffer_analytics')
        registry_file = os.path.join(analytics_dir, 'registry.json')
        
        if os.path.exists(registry_file):
            with open(registry_file, 'r') as f:
                registry = json.load(f)
        
        # Get datasets from memory first (most current data)
        for dataset_name, df in loaded_datasets.items():
            loaded_at = registry.get(dataset_name, {}).get('loaded_at', datetime.now().isoformat())
            dataset_info = {
                "name": dataset_name,
                "rows": len(df),
                "columns": list(df.columns),
                "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
                "loaded_at": loaded_at
            }
            datasets_info.append(dataset_info)
        
        # If memory is empty but registry exists, try to reload datasets
        if not datasets_info and registry:
            for dataset_name, registry_entry in registry.items():
                try:
                    # Try to reload the dataset to get current info
                    df = get_dataset(working_directory, dataset_name)
                    dataset_info = {
                        "name": dataset_name,
                        "rows": len(df),
                        "columns": list(df.columns),
                        "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2),
                        "loaded_at": registry_entry.get('loaded_at', datetime.now().isoformat())
                    }
                    datasets_info.append(dataset_info)
                except Exception:
                    # Skip datasets that can't be loaded (file may have been deleted)
                    continue
        
        # Return success result as JSON string
        result = {
            "status": "success",
            "datasets": datasets_info,
            "total_datasets": len(datasets_info)
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return f"Error: Failed to list datasets: {str(e)}"


# Schema for Google AI function declaration
schema_list_loaded_datasets = types.FunctionDeclaration(
    name="list_loaded_datasets",
    description="List all loaded datasets with their metadata including rows, columns, and memory usage",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},
        required=[],
    ),
)


# MCP Implementation Reference
# /Users/spaceship/project/analytic-agent-cli/function_bank/mcp_server/tools/list_loaded_datasets_tool.py
#
# async def list_loaded_datasets() -> dict:
#     """Show all datasets currently in memory."""
#     try:
#         datasets = []
#         total_memory = 0
#         
#         for name in DatasetManager.list_datasets():
#             info = DatasetManager.get_dataset_info(name)
#             memory_mb = info["memory_usage_mb"]
#             total_memory += memory_mb
#             
#             datasets.append({
#                 "name": name,
#                 "rows": info["shape"][0],
#                 "columns": info["shape"][1],
#                 "memory_mb": round(memory_mb, 1)
#             })
#         
#         return {
#             "loaded_datasets": datasets,
#             "total_datasets": len(datasets),
#             "total_memory_mb": round(total_memory, 1)
#         }
#         
#     except Exception as e:
#         return {"error": f"Failed to list datasets: {str(e)}}"