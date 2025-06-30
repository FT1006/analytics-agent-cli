"""Dataset loading tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig
from google.genai import types


def load_dataset(working_directory: str, file_path: str, dataset_name: str, sample_size: Optional[int] = None) -> dict:
    """Load any JSON/CSV dataset into memory with automatic schema discovery."""
    try:
        result = DatasetManager.load_dataset(file_path, dataset_name)
        
        # Apply sampling if requested
        if sample_size and sample_size < result["rows"]:
            df = DatasetManager.get_dataset(dataset_name)
            sampled_df = df.sample(n=sample_size, random_state=42)
            loaded_datasets[dataset_name] = sampled_df
            
            # Update schema for sampled data
            schema = dataset_schemas[dataset_name]
            schema.row_count = len(sampled_df)
            
            result["rows"] = len(sampled_df)
            result["sampled"] = True
            result["original_rows"] = len(df)
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load dataset: {str(e)}"
        }


# Gemini function schema
schema_load_dataset = types.FunctionDeclaration(
    name="load_dataset",
    description="Load any JSON/CSV dataset into memory with automatic schema discovery",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to the dataset file (JSON or CSV format)",
            ),
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name to assign to the loaded dataset for future reference",
            ),
            "sample_size": types.Schema(
                type=types.Type.INTEGER,
                description="Optional number of rows to sample for large datasets",
            ),
        },
        required=["file_path", "dataset_name"],
    ),
)


"""
MCP Implementation Reference:
=============================
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas, ChartConfig

async def load_dataset(file_path: str, dataset_name: str, sample_size: Optional[int] = None) -> dict:
    \"\"\"Load any JSON/CSV dataset into memory with automatic schema discovery.\"\"\"
    try:
        result = DatasetManager.load_dataset(file_path, dataset_name)
        
        # Apply sampling if requested
        if sample_size and sample_size < result["rows"]:
            df = DatasetManager.get_dataset(dataset_name)
            sampled_df = df.sample(n=sample_size, random_state=42)
            loaded_datasets[dataset_name] = sampled_df
            
            # Update schema for sampled data
            schema = dataset_schemas[dataset_name]
            schema.row_count = len(sampled_df)
            
            result["rows"] = len(sampled_df)
            result["sampled"] = True
            result["original_rows"] = len(df)
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load dataset: {str(e)}"
        }
"""