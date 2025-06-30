"""Dashboard generation tool implementation."""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from ..models.schemas import DatasetManager, loaded_datasets, dataset_schemas
from google.genai import types


def generate_dashboard(working_directory: str, dataset_name: str, chart_configs: List[Dict[str, Any]]) -> dict:
    """Generate multi-chart dashboards from any data."""
    try:
        df = DatasetManager.get_dataset(dataset_name)
        
        if not chart_configs:
            return {"error": "No chart configurations provided"}
        
        dashboard_results = {
            "dataset": dataset_name,
            "dashboard_generated": datetime.now().isoformat(),
            "charts": [],
            "dashboard_file": None
        }
        
        # Import here to avoid circular imports
        from .pandas_tools import create_chart
        
        # Generate each chart
        for i, config in enumerate(chart_configs):
            try:
                chart_result = create_chart(
                    working_directory,
                    dataset_name=dataset_name,
                    chart_type=config.get("chart_type", "bar"),
                    x_column=config["x_column"],
                    y_column=config.get("y_column"),
                    groupby_column=config.get("groupby_column"),
                    title=config.get("title"),
                    save_path=f"outputs/charts/dashboard_{dataset_name}_chart_{i+1}"
                )
                
                if "error" not in chart_result:
                    dashboard_results["charts"].append({
                        "chart_id": i+1,
                        "config": config,
                        "result": chart_result,
                        "status": "success"
                    })
                else:
                    dashboard_results["charts"].append({
                        "chart_id": i+1,
                        "config": config,
                        "error": chart_result["error"],
                        "status": "failed"
                    })
                    
            except Exception as chart_error:
                dashboard_results["charts"].append({
                    "chart_id": i+1,
                    "config": config,
                    "error": str(chart_error),
                    "status": "failed"
                })
        
        # Count successful charts
        successful_charts = len([c for c in dashboard_results["charts"] if c["status"] == "success"])
        failed_charts = len([c for c in dashboard_results["charts"] if c["status"] == "failed"])
        
        dashboard_results.update({
            "summary": {
                "total_charts": len(chart_configs),
                "successful_charts": successful_charts,
                "failed_charts": failed_charts
            }
        })
        
        return dashboard_results
        
    except Exception as e:
        return {"error": f"Dashboard generation failed: {str(e)}"}


# Gemini function schema
schema_generate_dashboard = types.FunctionDeclaration(
    name="generate_dashboard",
    description="Generate multi-chart dashboards from any data",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "dataset_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the dataset to visualize",
            ),
            "chart_configs": types.Schema(
                type=types.Type.ARRAY,
                description="List of chart configurations",
                items=types.Schema(type=types.Type.OBJECT),
            ),
        },
        required=["dataset_name", "chart_configs"],
    ),
)