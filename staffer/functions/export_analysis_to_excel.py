"""
Export analysis results to Excel format.

This function bridges Analytics → Excel workflows by taking analysis results
and converting them to Excel format using the existing write_data_to_excel function.
"""

import json
import os
from typing import Dict, Any, List, Union
from google.genai import types
from .write_data_to_excel import write_data_to_excel


def export_analysis_to_excel(
    working_directory: str,
    analysis_results: Dict[str, Any],
    file_path: str,
    sheet_name: str = "Analysis"
) -> str:
    """
    Export analysis results to Excel format.
    
    Args:
        working_directory: Base directory for file operations
        analysis_results: Dictionary containing analysis results
        file_path: Target Excel file path (relative to working_directory)
        sheet_name: Name of the Excel sheet (default: "Analysis")
    
    Returns:
        JSON string containing export status and metadata
    """
    try:
        # Validate working directory
        if not os.path.exists(working_directory):
            return json.dumps({
                "status": "error",
                "error": "Working directory does not exist"
            })
        
        # Security check: ensure file path doesn't escape working directory
        if ".." in file_path or file_path.startswith("/"):
            return json.dumps({
                "status": "error",
                "error": "Invalid file path: path must be relative and within working directory"
            })
        
        # Handle empty analysis results
        if not analysis_results:
            # Write empty data for empty results
            empty_data = [["Message"], ["No analysis results to export"]]
            write_result = write_data_to_excel(
                working_directory, file_path, sheet_name, empty_data
            )
            
            return json.dumps({
                "status": "exported",
                "file_path": file_path,
                "sheet_name": sheet_name,
                "rows_written": 0,
                "analysis_type": "empty"
            })
        
        # Detect analysis type
        analysis_type = analysis_results.get("analysis_type", "generic")
        
        # Convert analysis results to list of lists based on type
        main_data = _convert_to_data_rows(analysis_results, analysis_type)
        
        # Write main data to Excel
        write_result = write_data_to_excel(
            working_directory, file_path, sheet_name, main_data
        )
        
        # Parse write result to extract rows written
        rows_written = len(main_data) if main_data else 0
        
        # Create and write metadata sheet
        metadata_data = _create_metadata_rows(analysis_results, analysis_type)
        write_data_to_excel(
            working_directory, file_path, "Metadata", metadata_data
        )
        
        return json.dumps({
            "status": "exported",
            "file_path": file_path,
            "sheet_name": sheet_name,
            "rows_written": rows_written,
            "analysis_type": analysis_type
        })
        
    except Exception as e:
        return json.dumps({
            "status": "error",
            "error": f"Failed to export analysis: {str(e)}"
        })


def _convert_to_data_rows(analysis_results: Dict[str, Any], analysis_type: str) -> List[List[Any]]:
    """
    Convert analysis results to list of lists based on analysis type.
    
    Args:
        analysis_results: Dictionary containing analysis results
        analysis_type: Type of analysis (correlation, segmentation, etc.)
    
    Returns:
        List of lists suitable for Excel export
    """
    if analysis_type == "correlation":
        return _format_correlation_data(analysis_results)
    elif analysis_type == "segmentation":
        return _format_segmentation_data(analysis_results)
    elif analysis_type == "distribution":
        return _format_distribution_data(analysis_results)
    elif analysis_type == "time_series":
        return _format_time_series_data(analysis_results)
    else:
        return _format_generic_data(analysis_results)


def _format_correlation_data(results: Dict[str, Any]) -> List[List[Any]]:
    """Format correlation analysis results for Excel."""
    if "correlation_matrix" in results and "columns" in results:
        # Create correlation matrix as list of lists
        matrix = results["correlation_matrix"]
        columns = results["columns"]
        
        # Header row with empty cell for row labels, then column names
        data = [[""] + columns]
        
        # Data rows with row label and values
        for i, row in enumerate(matrix):
            data.append([columns[i]] + row)
        
        return data
    elif "strong_correlations" in results:
        # Create strong correlations table
        correlations = results["strong_correlations"]
        if correlations:
            # Get headers from first item
            headers = list(correlations[0].keys())
            data = [headers]
            
            # Add data rows
            for item in correlations:
                data.append([item.get(h, "") for h in headers])
            
            return data
        else:
            return [["No strong correlations found"]]
    else:
        # Fallback to generic format
        return _format_generic_data(results)


def _format_segmentation_data(results: Dict[str, Any]) -> List[List[Any]]:
    """Format segmentation analysis results for Excel."""
    if "segment_data" in results:
        segment_data = results["segment_data"]
        if segment_data:
            # Get headers from first item
            headers = list(segment_data[0].keys())
            data = [headers]
            
            # Add data rows
            for item in segment_data:
                data.append([item.get(h, "") for h in headers])
            
            # Add summary row if available
            if "summary" in results:
                summary = results["summary"]
                summary_row = ["TOTAL"] + [""] * (len(headers) - 1)
                
                # Fill in summary values where headers match
                for key, value in summary.items():
                    if key in headers:
                        idx = headers.index(key)
                        summary_row[idx] = value
                
                data.append(summary_row)
            
            return data
        else:
            return [["No segment data available"]]
    else:
        return _format_generic_data(results)


def _format_distribution_data(results: Dict[str, Any]) -> List[List[Any]]:
    """Format distribution analysis results for Excel."""
    if "distribution" in results:
        dist = results["distribution"]
        
        # Create distribution table
        data = [["Bin_Start", "Bin_End", "Count", "Percentage"]]
        bins = dist.get("bins", [])
        counts = dist.get("counts", [])
        percentages = dist.get("percentages", [])
        
        for i in range(len(counts)):
            bin_start = bins[i] if i < len(bins) else "N/A"
            bin_end = bins[i + 1] if i + 1 < len(bins) else "N/A"
            count = counts[i] if i < len(counts) else 0
            percentage = percentages[i] if i < len(percentages) else 0
            
            data.append([bin_start, bin_end, count, percentage])
        
        # Add statistics if available
        if "statistics" in results:
            stats = results["statistics"]
            
            # Add empty row separator
            data.append(["", "", "", ""])
            data.append(["Statistics", "", "", ""])
            
            for key, value in stats.items():
                data.append([key, value, "", ""])
        
        return data
    else:
        return _format_generic_data(results)


def _format_time_series_data(results: Dict[str, Any]) -> List[List[Any]]:
    """Format time series analysis results for Excel."""
    if "time_series" in results:
        ts = results["time_series"]
        
        data = [["Date", "Actual", "Forecast"]]
        dates = ts.get("dates", [])
        values = ts.get("values", [])
        forecast = ts.get("forecast", [])
        
        max_len = max(len(dates), len(values), len(forecast))
        
        for i in range(max_len):
            date = dates[i] if i < len(dates) else ""
            actual = values[i] if i < len(values) else ""
            forecast_val = forecast[i] if i < len(forecast) else ""
            
            data.append([date, actual, forecast_val])
        
        # Add seasonality info if available
        if "seasonality" in results:
            seasonality = results["seasonality"]
            
            # Add separator and seasonality info
            data.append(["", "", ""])
            data.append(["Seasonality", "", ""])
            
            for key, value in seasonality.items():
                data.append([key, value, ""])
        
        return data
    else:
        return _format_generic_data(results)


def _format_generic_data(results: Dict[str, Any]) -> List[List[Any]]:
    """Format generic analysis results for Excel."""
    # Look for common data structures
    if "data" in results and isinstance(results["data"], list):
        data_list = results["data"]
        if data_list and isinstance(data_list[0], dict):
            # Convert list of dicts to rows
            headers = list(data_list[0].keys())
            data = [headers]
            for item in data_list:
                data.append([item.get(h, "") for h in headers])
            return data
        else:
            # Simple list, convert to single column
            return [["Value"]] + [[str(item)] for item in data_list]
    
    # Flatten the dictionary into key-value pairs
    data = [["Metric", "Value", "Type"]]
    for key, value in results.items():
        if key == "analysis_type":
            continue
            
        if isinstance(value, (dict, list)):
            data.append([key, str(value), type(value).__name__])
        else:
            data.append([key, value, type(value).__name__])
    
    return data


def _create_metadata_rows(analysis_results: Dict[str, Any], analysis_type: str) -> List[List[Any]]:
    """Create metadata rows with analysis summary."""
    import datetime
    
    data = [["Property", "Value"]]
    data.append(["Analysis Type", analysis_type])
    data.append(["Total Keys", len(analysis_results)])
    data.append(["Export Timestamp", datetime.datetime.now().isoformat()])
    
    # Add specific metadata based on analysis type
    if analysis_type == "correlation" and "strong_correlations" in analysis_results:
        data.append(["Strong Correlations Count", len(analysis_results["strong_correlations"])])
    elif analysis_type == "segmentation" and "segment_data" in analysis_results:
        data.append(["Segments Count", len(analysis_results["segment_data"])])
    elif analysis_type == "distribution" and "distribution" in analysis_results:
        dist = analysis_results["distribution"]
        bins_count = len(dist.get("bins", [])) - 1 if dist.get("bins") else 0  # bins - 1 = actual bins
        data.append(["Distribution Bins", bins_count])
    
    # Add any custom metadata from results
    if "metadata" in analysis_results:
        custom_metadata = analysis_results["metadata"]
        for key, value in custom_metadata.items():
            data.append([f"Custom: {key}", str(value)])
    
    return data


# Schema for Google AI function declaration
schema_export_analysis_to_excel = types.FunctionDeclaration(
    name="export_analysis_to_excel",
    description="Export analysis results (correlations, segments, distributions, etc.) to Excel format using intelligent formatting",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "analysis_results": types.Schema(
                type=types.Type.OBJECT,
                description="Dictionary containing analysis results from analytics functions. Can include correlation matrices, segmentation data, distribution analysis, time series, or generic analysis results.",
            ),
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="Path to Excel file for export, relative to the working directory (e.g., 'analysis_results.xlsx')",
            ),
            "sheet_name": types.Schema(
                type=types.Type.STRING,
                description="Name of the Excel sheet to write to (default: 'Analysis')",
            ),
        },
        required=["analysis_results", "file_path"],
    ),
)