"""Get statistical summary of a loaded dataset"""
import json
import os
from typing import Optional
from google.genai import types
from .load_dataset import loaded_datasets, dataset_schemas


get_dataset_summary_schema = types.FunctionDeclaration(
    name="get_dataset_summary",
    description="Get statistical summary of a loaded dataset, including basic info, numerical statistics, categorical summaries, and missing data information",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the dataset to summarize",
            ),
        },
        required=["dataset_name"],
    ),
)


def get_dataset_summary(working_directory: str, dataset_name: Optional[str]) -> str:
    """Get statistical summary of a loaded dataset
    
    Args:
        working_directory: The working directory path
        dataset_name: Name of the dataset to summarize
        
    Returns:
        JSON string containing the dataset summary or error message
    """
    try:
        # Validate inputs
        if working_directory is None:
            return json.dumps({"error": "Working directory cannot be None"})
        
        if dataset_name is None:
            return json.dumps({"error": "Dataset name cannot be None"})
        
        # Check if dataset exists in memory
        if dataset_name not in loaded_datasets:
            return json.dumps({"error": f"Dataset '{dataset_name}' not found. Please load it first."})
        
        df = loaded_datasets[dataset_name]
        
        # Basic info
        summary = {
            "dataset_name": dataset_name,
            "shape": list(df.shape),
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
        }
        
        # Numerical summary
        numerical_cols = df.select_dtypes(include=['number']).columns.tolist()
        if numerical_cols:
            numerical_summary = {}
            stats_df = df[numerical_cols].describe()
            for col in numerical_cols:
                numerical_summary[col] = stats_df[col].to_dict()
            summary["numerical_summary"] = numerical_summary
        
        # Categorical summary
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if categorical_cols:
            categorical_summary = {}
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                categorical_summary[col] = {
                    "unique_count": df[col].nunique(),
                    "top_values": value_counts.head(5).to_dict(),
                    "null_count": int(df[col].isnull().sum())
                }
            summary["categorical_summary"] = categorical_summary
        
        # Missing data summary
        missing_counts = df.isnull().sum()
        columns_with_missing = missing_counts[missing_counts > 0].to_dict()
        # Convert numpy int64 to Python int
        columns_with_missing = {k: int(v) for k, v in columns_with_missing.items()}
        
        summary["missing_data"] = {
            "total_missing": int(missing_counts.sum()),
            "columns_with_missing": columns_with_missing
        }
        
        return json.dumps(summary)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to generate summary: {str(e)}"})


# MCP version reference:
# """Dataset summary resource implementation."""
# 
# from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
# from typing import Dict, Any, Optional
# 
# 
# async def get_dataset_summary(dataset_name: str) -> dict:
#     """Statistical summary (pandas.describe() equivalent)."""
#     try:
#         df = DatasetManager.get_dataset(dataset_name)
#         
#         # Get basic info
#         summary = {
#             "dataset_name": dataset_name,
#             "shape": df.shape,
#             "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024**2, 2)
#         }
#         
#         # Numerical summary
#         numerical_cols = df.select_dtypes(include=['number']).columns
#         if len(numerical_cols) > 0:
#             summary["numerical_summary"] = df[numerical_cols].describe().to_dict()
#         
#         # Categorical summary
#         categorical_cols = df.select_dtypes(include=['object', 'category']).columns
#         if len(categorical_cols) > 0:
#             summary["categorical_summary"] = {}
#             for col in categorical_cols:
#                 summary["categorical_summary"][col] = {
#                     "unique_count": df[col].nunique(),
#                     "top_values": df[col].value_counts().head(5).to_dict(),
#                     "null_count": df[col].isnull().sum()
#                 }
#         
#         # Missing data summary
#         missing_data = df.isnull().sum()
#         summary["missing_data"] = {
#             "total_missing": int(missing_data.sum()),
#             "columns_with_missing": missing_data[missing_data > 0].to_dict()
#         }
#         
#         return summary
#         
#     except Exception as e:
#         return {"error": f"Failed to generate summary: {str(e)}"}