"""JSON serialization utilities for pandas data types."""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Any, Dict, List, Union


def convert_pandas_types(obj: Any) -> Any:
    """Convert pandas/numpy types to JSON-serializable Python types."""
    
    # Handle pandas/numpy integers
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    
    # Handle pandas/numpy floats
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        if np.isnan(obj):
            return None  # Convert NaN to None instead of "NaN"
        return float(obj)
    
    # Handle pandas/numpy booleans
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    
    # Handle pandas Timestamp
    if isinstance(obj, pd.Timestamp):
        return obj.isoformat()
    
    # Handle datetime
    if isinstance(obj, datetime):
        return obj.isoformat()
    
    # Handle numpy arrays
    if isinstance(obj, np.ndarray):
        return [convert_pandas_types(item) for item in obj.tolist()]
    
    # Handle pandas Series
    if isinstance(obj, pd.Series):
        return {str(k): convert_pandas_types(v) for k, v in obj.to_dict().items()}
    
    # Handle pandas DataFrame
    if isinstance(obj, pd.DataFrame):
        return {
            str(col): convert_pandas_types(obj[col].to_dict()) 
            for col in obj.columns
        }
    
    # Handle dictionaries recursively
    if isinstance(obj, dict):
        return {
            str(k): convert_pandas_types(v) 
            for k, v in obj.items()
        }
    
    # Handle lists recursively  
    if isinstance(obj, list):
        return [convert_pandas_types(item) for item in obj]
    
    # Handle tuples
    if isinstance(obj, tuple):
        return [convert_pandas_types(item) for item in obj]
    
    # Return as-is for basic Python types
    return obj


def safe_json_return(data: Any) -> Dict[str, Any]:
    """Safely convert any data structure to JSON-serializable format."""
    try:
        # Convert pandas types first
        converted_data = convert_pandas_types(data)
        
        # Test if it's actually JSON serializable
        json.dumps(converted_data)
        
        return converted_data
    
    except (TypeError, ValueError) as e:
        # If conversion fails, return error info
        return {
            "error": f"JSON serialization failed: {str(e)}",
            "data_type": str(type(data)),
            "data_preview": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
        }


def sanitize_for_json(obj: Any) -> Any:
    """Sanitize object for JSON serialization, handling common pandas issues."""
    
    if obj is None or obj is pd.NaType:
        return None
    
    if pd.isna(obj):
        return None
        
    if isinstance(obj, (np.integer, np.int64, np.int32, np.int16, np.int8)):
        return int(obj)
        
    if isinstance(obj, (np.floating, np.float64, np.float32, np.float16)):
        if np.isnan(obj) or np.isinf(obj):
            return None
        return float(obj)
        
    if isinstance(obj, np.bool_):
        return bool(obj)
        
    if isinstance(obj, pd.Timestamp):
        return obj.strftime('%Y-%m-%d %H:%M:%S')
        
    if isinstance(obj, (pd.Series, pd.DataFrame)):
        return obj.to_dict()
        
    return obj