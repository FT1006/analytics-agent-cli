"""Suggest analyses function for Staffer."""

import json
from typing import Dict, Any, Optional
from google.genai import types
from ..tools.load_dataset import loaded_datasets, dataset_schemas


def suggest_analyses(working_directory: str, dataset_name: str) -> str:
    """
    Suggest appropriate analysis types based on loaded dataset characteristics.
    
    Args:
        working_directory: The working directory path
        dataset_name: Name of the loaded dataset to analyze
        
    Returns:
        JSON string containing suggested analyses and dataset summary
    """
    try:
        if working_directory is None:
            return "Error: Working directory cannot be None"
        
        if dataset_name is None:
            return "Error: Dataset name cannot be None"
        
        if dataset_name not in dataset_schemas:
            return f"Error: Dataset '{dataset_name}' not found. Please load the dataset first."
            
        schema = dataset_schemas[dataset_name]
        
        # Get columns by type
        numerical_cols = [name for name, info in schema['columns'].items() 
                         if info['suggested_role'] == 'numerical']
        categorical_cols = [name for name, info in schema['columns'].items() 
                           if info['suggested_role'] == 'categorical']
        temporal_cols = [name for name, info in schema['columns'].items() 
                        if info['suggested_role'] == 'temporal']
        
        available_analyses = []
        
        # Basic analyses always available
        available_analyses.extend([
            {
                "type": "data_quality_assessment",
                "description": "Comprehensive data quality report",
                "requirements": "Any dataset",
                "tool": "validate_data_quality"
            },
            {
                "type": "distribution_analysis", 
                "description": "Analyze column distributions",
                "requirements": "Any columns",
                "tool": "analyze_distributions"
            }
        ])
        
        # Conditional analyses based on column types
        if len(numerical_cols) >= 2:
            available_analyses.append({
                "type": "correlation_analysis",
                "description": f"Find relationships between {len(numerical_cols)} numerical variables",
                "requirements": "2+ numerical columns",
                "tool": "find_correlations",
                "applicable_columns": numerical_cols
            })
            
            available_analyses.append({
                "type": "outlier_detection",
                "description": "Detect outliers in numerical data",
                "requirements": "Numerical columns",
                "tool": "detect_outliers",
                "applicable_columns": numerical_cols
            })
        
        if categorical_cols:
            available_analyses.append({
                "type": "segmentation",
                "description": f"Group data by {len(categorical_cols)} categorical variables",
                "requirements": "Categorical columns",
                "tool": "segment_by_column",
                "applicable_columns": categorical_cols
            })
        
        if temporal_cols and numerical_cols:
            available_analyses.append({
                "type": "time_series",
                "description": f"Analyze trends over time",
                "requirements": "Date + numerical columns",
                "tool": "time_series_analysis",
                "applicable_columns": {"date_columns": temporal_cols, "value_columns": numerical_cols}
            })
        
        if dataset_name in loaded_datasets and len(loaded_datasets[dataset_name]) > 1:
            available_analyses.append({
                "type": "feature_importance",
                "description": "Calculate feature importance for prediction",
                "requirements": "Numerical target + feature columns",
                "tool": "calculate_feature_importance"
            })
        
        return json.dumps({
            "status": "success",
            "dataset_name": dataset_name,
            "available_analyses": available_analyses,
            "dataset_summary": {
                "numerical_columns": len(numerical_cols),
                "categorical_columns": len(categorical_cols),
                "temporal_columns": len(temporal_cols),
                "total_rows": schema['row_count']
            }
        })
        
    except Exception as e:
        return f"Error: Failed to suggest analyses: {str(e)}"


# Schema for Google AI function declaration
suggest_analyses_schema = types.FunctionDeclaration(
    name="suggest_analyses",
    description="Suggest appropriate analysis types based on loaded dataset characteristics",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the loaded dataset to analyze",
            ),
        },
        required=["dataset_name"],
    ),
)


# MCP version (from /Users/spaceship/project/analytic-agent-cli/function_bank/mcp_server/resources/get_available_analyses_resource.py):
"""
async def get_available_analyses(dataset_name: Optional[str] = None) -> dict:
    \"\"\"List of applicable analysis types for current data.\"\"\"
    try:
        if dataset_name is None:
            datasets = DatasetManager.list_datasets()
            if not datasets:
                return {"error": "No datasets loaded"}
            dataset_name = datasets[-1]  # Use most recent
        
        if dataset_name not in dataset_schemas:
            return {"error": f"Dataset '{dataset_name}' not loaded"}
            
        schema = dataset_schemas[dataset_name]
        
        # Get columns by type
        numerical_cols = [name for name, info in schema['columns'].items() 
                         if info['suggested_role'] == 'numerical']
        categorical_cols = [name for name, info in schema['columns'].items() 
                           if info['suggested_role'] == 'categorical']
        temporal_cols = [name for name, info in schema['columns'].items() 
                        if info['suggested_role'] == 'temporal']
        
        available_analyses = []
        
        # Basic analyses always available
        available_analyses.extend([
            {
                "type": "data_quality_assessment",
                "description": "Comprehensive data quality report",
                "requirements": "Any dataset",
                "tool": "validate_data_quality"
            },
            {
                "type": "distribution_analysis", 
                "description": "Analyze column distributions",
                "requirements": "Any columns",
                "tool": "analyze_distributions"
            }
        ])
        
        # Conditional analyses based on column types
        if len(numerical_cols) >= 2:
            available_analyses.append({
                "type": "correlation_analysis",
                "description": f"Find relationships between {len(numerical_cols)} numerical variables",
                "requirements": "2+ numerical columns",
                "tool": "find_correlations",
                "applicable_columns": numerical_cols
            })
            
            available_analyses.append({
                "type": "outlier_detection",
                "description": "Detect outliers in numerical data",
                "requirements": "Numerical columns",
                "tool": "detect_outliers",
                "applicable_columns": numerical_cols
            })
        
        if categorical_cols:
            available_analyses.append({
                "type": "segmentation",
                "description": f"Group data by {len(categorical_cols)} categorical variables",
                "requirements": "Categorical columns",
                "tool": "segment_by_column",
                "applicable_columns": categorical_cols
            })
        
        if temporal_cols and numerical_cols:
            available_analyses.append({
                "type": "time_series",
                "description": f"Analyze trends over time",
                "requirements": "Date + numerical columns",
                "tool": "time_series_analysis",
                "applicable_columns": {"date_columns": temporal_cols, "value_columns": numerical_cols}
            })
        
        if len(df := DatasetManager.get_dataset(dataset_name)) > 1:
            available_analyses.append({
                "type": "feature_importance",
                "description": "Calculate feature importance for prediction",
                "requirements": "Numerical target + feature columns",
                "tool": "calculate_feature_importance"
            })
        
        return {
            "dataset_name": dataset_name,
            "available_analyses": available_analyses,
            "dataset_summary": {
                "numerical_columns": len(numerical_cols),
                "categorical_columns": len(categorical_cols),
                "temporal_columns": len(temporal_cols),
                "total_rows": schema['row_count']
            }
        }
        
    except Exception as e:
        return {"error": f"Failed to get available analyses: {str(e)}"}
"""