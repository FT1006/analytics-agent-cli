"""Custom analytics code execution tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from google.genai import types


def execute_custom_analytics_code(working_directory: str, dataset_name: str, python_code: str) -> str:
    """
    Execute custom Python code against a loaded dataset.
    
    Implementation steps:
    1. Get dataset from DatasetManager
    2. Serialize dataset to JSON for subprocess
    3. Wrap user code in execution template
    4. Execute via subprocess with uv run python -c
    5. Capture and return stdout/stderr
    """
    import subprocess
    import json
    
    try:
        # Step 1: Get dataset
        df = DatasetManager.get_dataset(dataset_name)
        
        # Step 2: Serialize dataset
        dataset_json = df.to_json(orient='records')
        
        # Step 3: Create execution template
        # Need to properly indent user code
        import textwrap
        indented_user_code = textwrap.indent(python_code, '    ')
        
        execution_code = f'''
import pandas as pd
import numpy as np
import plotly.express as px
import json

try:
    # Load dataset
    dataset_data = {dataset_json}
    df = pd.DataFrame(dataset_data)
    
    # Execute user code
{indented_user_code}
    
except Exception as e:
    print(f"ERROR: {{type(e).__name__}}: {{str(e)}}")
    import traceback
    print("Traceback:")
    print(traceback.format_exc())
'''
        
        # Step 4: Execute subprocess
        process = subprocess.run(
            ['uv', 'run', '--with', 'pandas', '--with', 'numpy', '--with', 'plotly',
             'python', '-c', execution_code],
            capture_output=True,
            text=True,
            timeout=30.0
        )
        
        # Step 5: Get output
        return process.stdout + process.stderr
            
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Code execution exceeded 30 second limit"
    except Exception as e:
        return f"EXECUTION ERROR: {type(e).__name__}: {str(e)}"


# Gemini function schema
schema_execute_custom_analytics_code = types.FunctionDeclaration(
    name="execute_custom_analytics_code",
    description="Execute custom Python code against a loaded dataset",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the dataset to run code against",
            ),
            "python_code": types.Schema(
                type=types.Type.STRING,
                description="Python code to execute. The dataset will be available as 'df'",
            ),
        },
        required=["dataset_name", "python_code"],
    ),
)