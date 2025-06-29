"""Get dataset context analytic function for Staffer."""

import os
import json
from google.genai import types
from ..tools.load_dataset import loaded_datasets, dataset_schemas


def get_dataset_context(working_directory):
    """List all datasets currently in memory with their context information."""
    try:
        # Validate working directory
        if working_directory is None:
            return "Error: Working directory cannot be None"
        
        datasets = []
        total_memory = 0
        
        # Check if we have any loaded datasets
        if not loaded_datasets:
            # Try to reload from persistence
            _reload_datasets_from_persistence(working_directory)
        
        # Build context for each loaded dataset
        for name, df in loaded_datasets.items():
            # Get schema info
            schema = dataset_schemas.get(name, {})
            
            # Calculate memory usage
            memory_mb = df.memory_usage(deep=True).sum() / (1024 * 1024)
            total_memory += memory_mb
            
            # Count column types from schema
            column_types = {"numerical": 0, "categorical": 0, "temporal": 0, "identifier": 0}
            
            if "columns" in schema:
                for col_info in schema["columns"].values():
                    role = col_info.get("suggested_role", "categorical")
                    if role in column_types:
                        column_types[role] += 1
            
            datasets.append({
                "name": name,
                "rows": len(df),
                "columns": len(df.columns),
                "memory_mb": round(memory_mb, 1),
                "column_types": column_types
            })
        
        # Build result
        result = {
            "datasets": datasets,
            "total_datasets": len(datasets),
            "total_memory_mb": round(total_memory, 1),
            "status": "loaded" if datasets else "empty"
        }
        
        return json.dumps(result)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to get dataset context: {str(e)}"})


def _reload_datasets_from_persistence(working_directory):
    """Helper function to reload datasets from persistence storage."""
    try:
        analytics_dir = os.path.join(working_directory, '.staffer_analytics')
        registry_file = os.path.join(analytics_dir, 'registry.json')
        
        if not os.path.exists(registry_file):
            return
        
        with open(registry_file, 'r') as f:
            registry = json.load(f)
        
        # Reload each dataset from the registry
        datasets_dir = os.path.join(analytics_dir, 'datasets')
        schemas_dir = os.path.join(analytics_dir, 'schemas')
        
        for dataset_name in registry.keys():
            # Load dataset
            dataset_file = os.path.join(datasets_dir, f'{dataset_name}.csv')
            if os.path.exists(dataset_file):
                import pandas as pd
                df = pd.read_csv(dataset_file)
                loaded_datasets[dataset_name] = df
                
                # Load schema
                schema_file = os.path.join(schemas_dir, f'{dataset_name}.json')
                if os.path.exists(schema_file):
                    with open(schema_file, 'r') as f:
                        dataset_schemas[dataset_name] = json.load(f)
                        
    except Exception:
        # Silently fail - persistence is optional
        pass


# Schema for Google AI function declaration
schema_get_dataset_context = types.FunctionDeclaration(
    name="get_dataset_context",
    description="Get context information about all currently loaded datasets including row counts, column counts, memory usage, and column type distributions",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={},
        required=[],
    ),
)

# MCP version reference:
# async def get_loaded_datasets() -> dict:
#     """List all datasets currently in memory."""
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
#                 "memory_mb": round(memory_mb, 1),
#                 "column_types": {
#                     role: len([c for c, col_info in info["schema"]["columns"].items() 
#                              if col_info["suggested_role"] == role])
#                     for role in ["numerical", "categorical", "temporal", "identifier"]
#                 }
#             })
#         
#         return {
#             "datasets": datasets,
#             "total_datasets": len(datasets),
#             "total_memory_mb": round(total_memory, 1),
#             "status": "loaded" if datasets else "empty"
#         }
#         
#     except Exception as e:
#         return {"error": f"Failed to list datasets: {str(e)}"}