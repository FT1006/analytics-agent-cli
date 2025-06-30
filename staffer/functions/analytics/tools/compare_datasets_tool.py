"""Dataset comparison tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from google.genai import types


def compare_datasets(working_directory: str, dataset_a: str, dataset_b: str, common_columns: Optional[List[str]] = None) -> dict:
    """Compare multiple datasets."""
    try:
        df_a = DatasetManager.get_dataset(dataset_a)
        df_b = DatasetManager.get_dataset(dataset_b)
        
        # Find common columns if not specified
        if common_columns is None:
            common_columns = list(set(df_a.columns) & set(df_b.columns))
        
        if not common_columns:
            return {"error": "No common columns found between datasets"}
        
        comparison = {
            "dataset_a": dataset_a,
            "dataset_b": dataset_b,
            "shape_comparison": {
                "dataset_a_shape": df_a.shape,
                "dataset_b_shape": df_b.shape,
                "row_difference": df_a.shape[0] - df_b.shape[0],
                "column_difference": df_a.shape[1] - df_b.shape[1]
            },
            "common_columns": common_columns,
            "column_comparisons": {}
        }
        
        # Compare each common column
        for col in common_columns:
            col_comparison = {
                "column": col,
                "dtype_a": str(df_a[col].dtype),
                "dtype_b": str(df_b[col].dtype),
                "unique_values_a": df_a[col].nunique(),
                "unique_values_b": df_b[col].nunique(),
                "null_pct_a": round(df_a[col].isnull().mean() * 100, 2),
                "null_pct_b": round(df_b[col].isnull().mean() * 100, 2)
            }
            
            # Numerical comparison
            if pd.api.types.is_numeric_dtype(df_a[col]) and pd.api.types.is_numeric_dtype(df_b[col]):
                col_comparison.update({
                    "mean_a": round(df_a[col].mean(), 3),
                    "mean_b": round(df_b[col].mean(), 3),
                    "mean_difference": round(df_a[col].mean() - df_b[col].mean(), 3),
                    "std_a": round(df_a[col].std(), 3),
                    "std_b": round(df_b[col].std(), 3)
                })
            
            comparison["column_comparisons"][col] = col_comparison
        
        return comparison
        
    except Exception as e:
        return {"error": f"Dataset comparison failed: {str(e)}"}


# Gemini function schema
schema_compare_datasets = types.FunctionDeclaration(
    name="compare_datasets",
    description="Compare multiple datasets",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_a": types.Schema(
                type=types.Type.STRING,
                description="Name of the first dataset to compare",
            ),
            "dataset_b": types.Schema(
                type=types.Type.STRING,
                description="Name of the second dataset to compare",
            ),
            "common_columns": types.Schema(
                type=types.Type.ARRAY,
                description="List of common column names to compare (optional - if not provided, all common columns will be compared)",
                items=types.Schema(type=types.Type.STRING),
            ),
        },
        required=["dataset_a", "dataset_b"],
    ),
)