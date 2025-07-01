# Analytics Functions Reference

This document provides comprehensive documentation for all 36 analytics functions available in the Analytic Agent CLI.

## Overview

The analytics functions are organized into three categories:
- **Tools (17)**: Core data analysis and manipulation functions
- **Resources (10)**: Data access and metadata functions  
- **Prompts (9)**: AI-assisted analysis and consultation functions

---

# TOOLS (17 Functions)

Tools provide direct functionality for data analysis, visualization, and manipulation.

## load_dataset

**Category**: Tool
**Purpose**: Load CSV or JSON datasets into memory with automatic schema discovery
**Use Case**: Import data files for analysis, with optional sampling for large datasets

### Parameters
- `file_path` (str): Path to the dataset file (JSON or CSV format)
- `dataset_name` (str): Name to assign to the loaded dataset for future reference
- `sample_size` (int, optional): Number of rows to sample for large datasets

### Returns
- `dict`: Dataset loading status and metadata including rows, columns, memory usage

### Example Usage
```python
# Load a complete dataset
result = load_dataset(working_directory="/path/to/data", file_path="sales_data.csv", dataset_name="sales")
print(result)

# Load a sampled dataset for large files
result = load_dataset(working_directory="/path/to/data", file_path="large_dataset.csv", dataset_name="sample_data", sample_size=1000)
```

### Sample Output
```json
{
  "status": "success",
  "dataset_name": "sales",
  "rows": 1500,
  "columns": 8,
  "memory_usage_mb": 2.3,
  "sampled": false
}
```

---

## list_loaded_datasets

**Category**: Tool
**Purpose**: Show all datasets currently in memory with size and shape information
**Use Case**: Monitor loaded datasets and memory usage

### Parameters
None

### Returns
- `dict`: List of loaded datasets with rows, columns, and memory usage

### Example Usage
```python
result = list_loaded_datasets(working_directory="/path/to/data")
print(result)
```

### Sample Output
```json
{
  "loaded_datasets": [
    {"name": "sales", "rows": 1500, "columns": 8, "memory_mb": 2.3},
    {"name": "customers", "rows": 800, "columns": 5, "memory_mb": 1.1}
  ],
  "total_datasets": 2,
  "total_memory_mb": 3.4
}
```

---

## analyze_distributions

**Category**: Tool
**Purpose**: Analyze the distribution of any column (numerical or categorical)
**Use Case**: Understand data patterns, identify skewness, outliers, and distribution characteristics

### Parameters
- `dataset_name` (str): Name of the dataset to analyze
- `column_name` (str): Name of the column to analyze

### Returns
- `dict`: Distribution statistics including mean, median, quartiles for numerical data or frequency counts for categorical data

### Example Usage
```python
# Analyze numerical column distribution
result = analyze_distributions(working_directory="/path/to/data", dataset_name="sales", column_name="revenue")
print(result)

# Analyze categorical column distribution  
result = analyze_distributions(working_directory="/path/to/data", dataset_name="sales", column_name="product_category")
```

### Sample Output
```json
{
  "dataset": "sales",
  "column": "revenue",
  "distribution_type": "numerical",
  "mean": 15420.5,
  "median": 12000.0,
  "std": 8500.3,
  "quartiles": {"q25": 8000.0, "q50": 12000.0, "q75": 20000.0},
  "skewness": 1.2,
  "kurtosis": 0.8
}
```

---

## calculate_feature_importance

**Category**: Tool
**Purpose**: Calculate feature importance for predictive modeling using correlation analysis
**Use Case**: Identify which variables are most predictive of a target outcome

### Parameters
- `dataset_name` (str): Name of the dataset to analyze
- `target_column` (str): Name of the target column for prediction
- `feature_columns` (list, optional): List of feature column names (if not provided, all other columns will be used)

### Returns
- `dict`: Feature importance rankings with correlation values and rankings

### Example Usage
```python
# Calculate feature importance for revenue prediction
result = calculate_feature_importance(
    working_directory="/path/to/data",
    dataset_name="sales", 
    target_column="revenue",
    feature_columns=["marketing_spend", "sales_calls", "lead_score"]
)
print(result)
```

### Sample Output
```json
{
  "dataset": "sales",
  "target_column": "revenue",
  "method": "correlation_based",
  "feature_importance": {
    "marketing_spend": {"correlation": 0.85, "importance": 0.85, "rank": 1},
    "lead_score": {"correlation": 0.72, "importance": 0.72, "rank": 2}
  },
  "top_features": ["marketing_spend", "lead_score"]
}
```

---

## compare_datasets

**Category**: Tool
**Purpose**: Compare multiple datasets to identify differences in structure and values
**Use Case**: Analyze dataset compatibility, track changes between versions, or merge preparation

### Parameters
- `dataset_a` (str): Name of the first dataset to compare
- `dataset_b` (str): Name of the second dataset to compare
- `common_columns` (list, optional): List of common column names to compare (if not provided, all common columns will be compared)

### Returns
- `dict`: Detailed comparison including shape differences and column-by-column analysis

### Example Usage
```python
result = compare_datasets(
    working_directory="/path/to/data",
    dataset_a="sales_q1", 
    dataset_b="sales_q2",
    common_columns=["revenue", "product", "region"]
)
print(result)
```

### Sample Output
```json
{
  "dataset_a": "sales_q1",
  "dataset_b": "sales_q2", 
  "shape_comparison": {
    "dataset_a_shape": [1500, 8],
    "dataset_b_shape": [1200, 8],
    "row_difference": 300
  },
  "column_comparisons": {
    "revenue": {"mean_a": 15000, "mean_b": 16500, "mean_difference": 1500}
  }
}
```

---

## create_chart

**Category**: Tool
**Purpose**: Create interactive HTML charts from loaded datasets for data visualization
**Use Case**: Generate publication-ready visualizations for analysis and reporting

### Parameters
- `dataset_name` (str): Name of the dataset to visualize
- `chart_type` (str): Type of chart to create (histogram, bar, scatter, line, box)
- `x_column` (str): Name of the column for x-axis
- `y_column` (str, optional): Name of the column for y-axis (optional for some chart types)
- `groupby_column` (str, optional): Name of the column to group by (optional)
- `title` (str, optional): Title for the chart (optional - will be auto-generated if not provided)
- `save_path` (str, optional): Path to save the chart file (optional)

### Returns
- `dict`: Chart creation status and file path

### Example Usage
```python
# Create a scatter plot
result = create_chart(
    working_directory="/path/to/data",
    dataset_name="sales",
    chart_type="scatter", 
    x_column="marketing_spend",
    y_column="revenue",
    title="Marketing Spend vs Revenue"
)
print(result)

# Create a grouped bar chart
result = create_chart(
    working_directory="/path/to/data", 
    dataset_name="sales",
    chart_type="bar",
    x_column="region", 
    y_column="revenue",
    groupby_column="product_category"
)
```

### Sample Output
```json
{
  "dataset": "sales",
  "chart_type": "scatter",
  "chart_config": {
    "x_column": "marketing_spend",
    "y_column": "revenue", 
    "title": "Marketing Spend vs Revenue"
  },
  "chart_file": "/path/outputs/charts/chart_sales_scatter_marketing_spend.html",
  "status": "success"
}
```

---

## detect_outliers

**Category**: Tool  
**Purpose**: Detect outliers in numerical data using configurable statistical methods
**Use Case**: Identify unusual values that may indicate data quality issues or interesting patterns

### Parameters
- `dataset_name` (str): Name of the dataset to analyze for outliers
- `columns` (list, optional): List of columns to analyze. If not specified, all numerical columns will be used
- `method` (str): Method for outlier detection: 'iqr' or 'zscore'

### Returns
- `dict`: Outlier analysis results including counts and bounds for each column

### Example Usage
```python
# Detect outliers using IQR method
result = detect_outliers(
    working_directory="/path/to/data",
    dataset_name="sales",
    columns=["revenue", "marketing_spend"],
    method="iqr"
)
print(result)

# Auto-detect outliers in all numerical columns using z-score
result = detect_outliers(working_directory="/path/to/data", dataset_name="sales", method="zscore")
```

### Sample Output
```json
{
  "dataset": "sales",
  "method": "iqr",
  "total_outliers": 23,
  "outliers_by_column": {
    "revenue": {
      "outlier_count": 15,
      "outlier_percentage": 1.2,
      "lower_bound": -5000,
      "upper_bound": 45000,
      "outlier_values": [50000, 55000, 48000]
    }
  }
}
```

---

## execute_custom_analytics_code

**Category**: Tool
**Purpose**: Execute custom Python code against a loaded dataset in a secure environment
**Use Case**: Run custom analysis, create specialized visualizations, or perform advanced statistical operations

### Parameters
- `dataset_name` (str): Name of the dataset to run code against
- `python_code` (str): Python code to execute. The dataset will be available as 'df'

### Returns
- `str`: Output from code execution including print statements and results

### Example Usage
```python
custom_code = """
# Calculate custom metrics
correlation = df['revenue'].corr(df['marketing_spend'])
print(f"Revenue-Marketing correlation: {correlation:.3f}")

# Create custom analysis
top_performers = df.nlargest(5, 'revenue')[['product', 'revenue']]
print("Top 5 products by revenue:")
print(top_performers)
"""

result = execute_custom_analytics_code(
    working_directory="/path/to/data",
    dataset_name="sales", 
    python_code=custom_code
)
print(result)
```

### Sample Output
```
Revenue-Marketing correlation: 0.847
Top 5 products by revenue:
     product  revenue
15   Product A    55000
28   Product B    52000
33   Product A    48000
```

---

## export_insights

**Category**: Tool
**Purpose**: Export comprehensive analysis results in multiple formats (JSON, CSV, HTML)
**Use Case**: Create reports for sharing, documentation, or presentation purposes

### Parameters
- `dataset_name` (str): Name of the dataset to export insights for
- `format` (str): Export format: 'json', 'csv', or 'html'
- `include_charts` (bool, optional): Whether to include charts in the export

### Returns
- `dict`: Export status and file location

### Example Usage
```python
# Export as HTML report
result = export_insights(
    working_directory="/path/to/data",
    dataset_name="sales",
    format="html",
    include_charts=True
)
print(result)

# Export as JSON for programmatic use
result = export_insights(working_directory="/path/to/data", dataset_name="sales", format="json")
```

### Sample Output
```json
{
  "dataset": "sales",
  "export_format": "html",
  "export_file": "/path/outputs/reports/insights_sales.html",
  "insights_summary": {
    "total_metrics": 15,
    "has_numerical_summary": true,
    "has_categorical_summary": true
  },
  "status": "success"
}
```

---

## find_correlations

**Category**: Tool
**Purpose**: Find statistical correlations between numerical columns
**Use Case**: Identify relationships between variables for feature selection or business insights

### Parameters
- `dataset_name` (str): Name of the dataset to analyze for correlations
- `columns` (list, optional): List of columns to analyze. If not specified, all numerical columns will be used
- `threshold` (float): Minimum correlation threshold to report (default 0.3)

### Returns
- `dict`: Correlation matrix and strong correlations above threshold

### Example Usage
```python
# Find all strong correlations
result = find_correlations(
    working_directory="/path/to/data",
    dataset_name="sales",
    threshold=0.5
)
print(result)

# Focus on specific columns
result = find_correlations(
    working_directory="/path/to/data",
    dataset_name="sales",
    columns=["revenue", "marketing_spend", "sales_calls"],
    threshold=0.3
)
```

### Sample Output
```json
{
  "dataset": "sales",
  "strong_correlations": [
    {
      "column_1": "revenue",
      "column_2": "marketing_spend",
      "correlation": 0.847,
      "strength": "strong",
      "direction": "positive"
    }
  ],
  "threshold": 0.5
}
```

---

## generate_dashboard

**Category**: Tool
**Purpose**: Generate multi-chart dashboards from datasets for comprehensive analysis
**Use Case**: Create executive dashboards, operational reports, or comprehensive data stories

### Parameters
- `dataset_name` (str): Name of the dataset to visualize
- `chart_configs` (list): List of chart configurations specifying chart types and columns

### Returns
- `dict`: Dashboard generation status with individual chart results

### Example Usage
```python
chart_configs = [
    {"chart_type": "bar", "x_column": "region", "y_column": "revenue"},
    {"chart_type": "scatter", "x_column": "marketing_spend", "y_column": "revenue"},
    {"chart_type": "histogram", "x_column": "revenue"}
]

result = generate_dashboard(
    working_directory="/path/to/data",
    dataset_name="sales",
    chart_configs=chart_configs
)
print(result)
```

### Sample Output
```json
{
  "dataset": "sales",
  "dashboard_generated": "2024-01-15T10:30:00",
  "summary": {
    "total_charts": 3,
    "successful_charts": 3,
    "failed_charts": 0
  },
  "charts": [
    {"chart_id": 1, "status": "success", "config": {"chart_type": "bar"}}
  ]
}
```

---

## memory_optimization_report

**Category**: Tool
**Purpose**: Analyze memory usage and suggest optimizations for datasets
**Use Case**: Optimize memory usage for large datasets or memory-constrained environments

### Parameters
- `dataset_name` (str): Name of the dataset to analyze for memory optimization

### Returns
- `dict`: Memory analysis and optimization suggestions

### Example Usage
```python
result = memory_optimization_report(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```json
{
  "dataset": "sales",
  "current_memory_usage": {"total_mb": 15.3},
  "optimization_suggestions": [
    {
      "column": "product_id",
      "suggestion": "Convert to categorical",
      "potential_savings_kb": 245.2
    }
  ],
  "potential_savings": {"total_mb": 3.2, "percentage": 21.0}
}
```

---

## merge_datasets

**Category**: Tool
**Purpose**: Join multiple datasets on common keys using various join strategies
**Use Case**: Combine related datasets for comprehensive analysis

### Parameters
- `dataset_configs` (list): List of dataset configurations to merge with join specifications
- `join_strategy` (str): Join strategy (inner, left, right, outer)

### Returns
- `dict`: Merge results including new dataset name and merge statistics

### Example Usage
```python
dataset_configs = [
    {"dataset_name": "sales", "join_column": "customer_id"},
    {"dataset_name": "customers", "join_column": "customer_id"}
]

result = merge_datasets(
    working_directory="/path/to/data",
    dataset_configs=dataset_configs,
    join_strategy="inner"
)
print(result)
```

### Sample Output
```json
{
  "merged_dataset_name": "merged_sales_customers",
  "merge_strategy": "inner",
  "final_shape": [1200, 13],
  "merge_steps": [
    {
      "merged_with": "customers",
      "join_column": "customer_id",
      "rows_gained": -300,
      "columns_gained": 5
    }
  ]
}
```

---

## segment_by_column

**Category**: Tool
**Purpose**: Perform generic segmentation analysis on any categorical column
**Use Case**: Analyze performance differences across groups, customer segments, or product categories

### Parameters
- `dataset_name` (str): Name of the dataset to segment
- `column_name` (str): Column to segment by
- `method` (str): Segmentation method (default: auto)
- `top_n` (int): Number of top segments to return (default: 10)

### Returns
- `dict`: Segmentation results with statistics for each segment

### Example Usage
```python
result = segment_by_column(
    working_directory="/path/to/data",
    dataset_name="sales",
    column_name="region",
    top_n=5
)
print(result)
```

### Sample Output
```json
{
  "dataset": "sales",
  "segmented_by": "region",
  "segment_count": 4,
  "segments": {
    "North": {"count": 450, "percentage": 30.0, "revenue_mean": 16500},
    "South": {"count": 380, "percentage": 25.3, "revenue_mean": 14200}
  },
  "total_rows": 1500
}
```

---

## suggest_analysis

**Category**: Tool
**Purpose**: Generate AI-powered analysis recommendations based on dataset characteristics
**Use Case**: Get guidance on which analyses to perform based on your data structure

### Parameters
- `dataset_name` (str): Name of the dataset to analyze

### Returns
- `dict`: Analysis suggestions with commands and priorities

### Example Usage
```python
result = suggest_analysis(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```json
{
  "dataset_name": "sales",
  "suggestions": [
    {
      "type": "correlation_analysis",
      "description": "Find relationships between 4 numerical variables",
      "priority": "high",
      "command": "find_correlations('sales')"
    },
    {
      "type": "segmentation", 
      "description": "Group data by 3 categorical variables",
      "priority": "high",
      "command": "segment_by_column('sales', 'region')"
    }
  ]
}
```

---

## time_series_analysis

**Category**: Tool
**Purpose**: Perform temporal analysis when date columns are detected
**Use Case**: Analyze trends, seasonality, and patterns in time-based data

### Parameters
- `dataset_name` (str): Name of the dataset to analyze
- `date_column` (str): Column containing date/time values
- `value_column` (str): Column containing values to analyze over time
- `frequency` (str): Frequency for time series aggregation (default: auto)

### Returns
- `dict`: Time series analysis including trend direction and statistics

### Example Usage
```python
result = time_series_analysis(
    working_directory="/path/to/data",
    dataset_name="sales",
    date_column="sale_date",
    value_column="revenue",
    frequency="M"
)
print(result)
```

### Sample Output
```json
{
  "dataset": "sales",
  "date_column": "sale_date",
  "value_column": "revenue",
  "frequency": "M",
  "date_range": {"start": "2023-01-01", "end": "2023-12-31", "days": 365},
  "trend": {"slope": 1250.5, "direction": "increasing"},
  "statistics": {"mean": 15420.0, "std": 3200.5}
}
```

---

## validate_data_quality

**Category**: Tool
**Purpose**: Perform comprehensive data quality assessment with scoring and recommendations
**Use Case**: Assess dataset reliability before analysis or identify data cleaning needs

### Parameters
- `dataset_name` (str): Name of the dataset to validate

### Returns
- `dict`: Comprehensive quality report with scores and recommendations

### Example Usage
```python
result = validate_data_quality(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```json
{
  "dataset_name": "sales",
  "total_rows": 1500,
  "quality_score": 87.3,
  "missing_data": {"email": 12.3, "phone": 8.7},
  "duplicate_rows": 5,
  "potential_issues": ["High missing data in email column"],
  "recommendations": ["Consider dropping columns with >50% missing data"]
}
```

---

# RESOURCES (10 Functions)

Resources provide dynamic data context and metadata about loaded datasets and system state.

## get_analysis_suggestions

**Category**: Resource
**Purpose**: Get AI-generated analysis recommendations for the current or specified dataset
**Use Case**: Discover what analyses are most appropriate for your data structure

### Parameters
- `dataset_name` (str, optional): Name of the dataset to get suggestions for (optional - uses most recent if not provided)

### Returns
- `dict`: Analysis suggestions with commands and priorities

### Example Usage
```python
result = get_analysis_suggestions(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```json
{
  "dataset_name": "sales",
  "suggestions": [
    {
      "type": "correlation_analysis",
      "description": "Find relationships between numerical variables",
      "priority": "high",
      "tool": "find_correlations"
    }
  ]
}
```

---

## get_available_analyses

**Category**: Resource
**Purpose**: List all applicable analysis types for current data structure
**Use Case**: Understand what analytical capabilities are available for your specific dataset

### Parameters
- `dataset_name` (str, optional): Name of the dataset to get available analyses for (optional - uses most recent if not provided)

### Returns
- `dict`: Available analyses with requirements and applicable columns

### Example Usage
```python
result = get_available_analyses(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```json
{
  "dataset_name": "sales",
  "available_analyses": [
    {
      "type": "correlation_analysis",
      "description": "Find relationships between 4 numerical variables",
      "requirements": "2+ numerical columns",
      "tool": "find_correlations"
    }
  ],
  "dataset_summary": {"numerical_columns": 4, "categorical_columns": 3}
}
```

---

## get_column_types

**Category**: Resource
**Purpose**: Get detailed column classification including data types and suggested analytical roles
**Use Case**: Understand how the system categorizes your columns for analysis planning

### Parameters
- `dataset_name` (str, optional): Name of the dataset to get column types for (optional - uses most recent if not provided)

### Returns
- `dict`: Column classification with types, uniqueness, and sample values

### Example Usage
```python
result = get_column_types(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```json
{
  "dataset_name": "sales",
  "column_classification": {
    "revenue": {
      "suggested_role": "numerical",
      "dtype": "float64",
      "unique_values": 1342,
      "null_percentage": 2.1,
      "sample_values": [15000, 22000, 18500]
    }
  },
  "type_summary": {"numerical": 4, "categorical": 3, "temporal": 1}
}
```

---

## get_current_dataset

**Category**: Resource
**Purpose**: Get information about the currently active dataset
**Use Case**: Quick check of what dataset is loaded and ready for analysis

### Parameters
None

### Returns
- `dict`: Current dataset information including shape and memory usage

### Example Usage
```python
result = get_current_dataset(working_directory="/path/to/data")
print(result)
```

### Sample Output
```json
{
  "current_dataset": "sales",
  "shape": [1500, 8],
  "memory_mb": 2.3,
  "all_loaded_datasets": ["sales", "customers"],
  "total_datasets": 2
}
```

---

## get_dataset_sample

**Category**: Resource
**Purpose**: Get sample rows from a dataset for quick data preview
**Use Case**: Quickly inspect data structure and content without loading the entire dataset

### Parameters
- `dataset_name` (str): Name of the dataset to sample
- `n_rows` (int): Number of rows to sample (default: 5)

### Returns
- `dict`: Sample data with column names and sample records

### Example Usage
```python
result = get_dataset_sample(working_directory="/path/to/data", dataset_name="sales", n_rows=3)
print(result)
```

### Sample Output
```json
{
  "dataset_name": "sales",
  "sample_size": 3,
  "total_rows": 1500,
  "columns": ["product", "revenue", "region", "date"],
  "sample_data": [
    {"product": "Product A", "revenue": 15000, "region": "North", "date": "2023-01-15"},
    {"product": "Product B", "revenue": 22000, "region": "South", "date": "2023-01-16"}
  ]
}
```

---

## get_dataset_schema

**Category**: Resource
**Purpose**: Get comprehensive schema information for any loaded dataset
**Use Case**: Understand dataset structure, column types, and suggested analyses

### Parameters
- `dataset_name` (str): Name of the dataset to get schema for

### Returns
- `dict`: Complete schema with columns organized by type and analysis suggestions

### Example Usage
```python
result = get_dataset_schema(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```json
{
  "dataset_name": "sales",
  "total_rows": 1500,
  "total_columns": 8,
  "columns_by_type": {
    "numerical": [
      {"name": "revenue", "dtype": "float64", "unique_values": 1342, "null_percentage": 2.1}
    ],
    "categorical": [
      {"name": "region", "dtype": "object", "unique_values": 4, "null_percentage": 0.0}
    ]
  },
  "suggested_analyses": ["correlation_analysis", "segmentation", "time_series"]
}
```

---

## get_dataset_summary

**Category**: Resource
**Purpose**: Get statistical summary equivalent to pandas.describe() with additional insights
**Use Case**: Quick statistical overview of numerical columns and categorical summaries

### Parameters
- `dataset_name` (str): Name of the dataset to summarize

### Returns
- `dict`: Statistical summary with numerical and categorical breakdowns

### Example Usage
```python
result = get_dataset_summary(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```json
{
  "dataset_name": "sales",
  "shape": [1500, 8],
  "memory_usage_mb": 2.3,
  "numerical_summary": {
    "revenue": {"mean": 15420.5, "std": 8500.3, "min": 1000, "max": 55000}
  },
  "categorical_summary": {
    "region": {"unique_count": 4, "top_values": {"North": 450, "South": 380}}
  },
  "missing_data": {"total_missing": 32, "columns_with_missing": {"email": 18}}
}
```

---

## get_loaded_datasets

**Category**: Resource
**Purpose**: Get detailed list of all datasets currently loaded in memory
**Use Case**: Monitor loaded datasets with memory usage and structure information

### Parameters
None

### Returns
- `dict`: Comprehensive list of loaded datasets with metadata

### Example Usage
```python
result = get_loaded_datasets(working_directory="/path/to/data")
print(result)
```

### Sample Output
```json
{
  "datasets": [
    {
      "name": "sales",
      "rows": 1500,
      "columns": 8,
      "memory_mb": 2.3,
      "column_types": {"numerical": 4, "categorical": 3, "temporal": 1}
    }
  ],
  "total_datasets": 1,
  "total_memory_mb": 2.3,
  "status": "loaded"
}
```

---

## get_memory_usage

**Category**: Resource
**Purpose**: Monitor memory usage of all loaded datasets with optimization recommendations
**Use Case**: Track memory consumption and get suggestions for memory optimization

### Parameters
None

### Returns
- `dict`: Memory usage breakdown with recommendations

### Example Usage
```python
result = get_memory_usage(working_directory="/path/to/data")
print(result)
```

### Sample Output
```json
{
  "datasets": [
    {
      "dataset": "sales",
      "memory_mb": 2.3,
      "rows": 1500,
      "memory_per_row_kb": 1.6
    }
  ],
  "total_memory_mb": 2.3,
  "dataset_count": 1,
  "memory_recommendations": ["Memory usage is optimal"]
}
```

---

# PROMPTS (9 Functions)

Prompts provide AI-assisted guidance and interactive workflows for data analysis planning.

## dataset_first_look

**Category**: Prompt
**Purpose**: Generate adaptive first-look analysis guide based on dataset characteristics
**Use Case**: Get oriented with a new dataset and understand analysis possibilities

### Parameters
- `dataset_name` (str): Name of the dataset to analyze

### Returns
- `str`: Interactive analysis guide with specific recommendations and commands

### Example Usage
```python
result = dataset_first_look(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```
Let's explore your **sales** dataset together! 

I can see you have **1,500 records** with **8 columns**:

📊 Numerical columns (4): revenue, marketing_spend, sales_calls, lead_score
→ Perfect for correlation analysis, statistical summaries, and trend analysis

🏷️ Categorical columns (3): region, product, sales_rep
→ Great for segmentation, group comparisons, and distribution analysis

🎯 Recommended starting points:
• Correlation Analysis: Explore relationships between revenue and marketing_spend
  Command: `find_correlations('sales')`
• Segmentation: Group by region to analyze revenue patterns
  Command: `segment_by_column('sales', 'region')`

What aspect of your **sales** data would you like to explore first?
```

---

## correlation_investigation

**Category**: Prompt
**Purpose**: Guide users through comprehensive correlation analysis workflow
**Use Case**: Get step-by-step guidance for finding and interpreting correlations

### Parameters
- `dataset_name` (str): Name of the dataset to investigate for correlations

### Returns
- `str`: Correlation analysis workflow guide with specific commands

### Example Usage
```python
result = correlation_investigation(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```
Let's explore **correlations** in your **sales** dataset!

📊 Available numerical columns (4):
• revenue: 1342 unique values, 2.1% missing
• marketing_spend: 856 unique values, 0.0% missing

🎯 Correlation analysis strategy:
1. Start broad: Find all significant correlations
   → `find_correlations('sales')`
2. Focus on strong relationships: Investigate correlations > 0.7
3. Create visualizations: Plot the strongest correlations
   → `create_chart('sales', 'scatter', 'marketing_spend', 'revenue')`

Ready to discover hidden relationships in your data?
```

---

## dashboard_design_consultation

**Category**: Prompt
**Purpose**: Plan comprehensive dashboards for specific audiences and use cases
**Use Case**: Get guidance on creating effective dashboards tailored to your audience

### Parameters
- `dataset_name` (str): Name of the dataset for dashboard design
- `audience` (str): Target audience for the dashboard (executive, operational, analytical, or general)

### Returns
- `str`: Dashboard design guide with layout suggestions and chart recommendations

### Example Usage
```python
result = dashboard_design_consultation(
    working_directory="/path/to/data",
    dataset_name="sales", 
    audience="executive"
)
print(result)
```

### Sample Output
```
📊 **Dashboard Design Consultation: sales**

Target Audience: executive

Let's design a compelling dashboard from your **1,500 records** that tells a clear story!

🎯 Dashboard design principles:

For Executive/Leadership Audience:
• High-level KPIs and trend indicators
• Exception-based reporting (what needs attention)
• Clean, simple visualizations with clear takeaways

📊 Dashboard component recommendations:
1. Key Performance Indicators (KPIs)
   • Primary metrics from: revenue, marketing_spend, sales_calls
2. Trend Analysis
   • Time series charts showing revenue over sale_date

🎨 Dashboard layout suggestions for executive:
• Top row: 3-4 key KPIs with trend indicators
• Second row: Main performance chart (trend over time)
• Bottom rows: Segmentation breakdown and key insights
```

---

## data_quality_assessment

**Category**: Prompt
**Purpose**: Guide systematic data quality review with specific recommendations
**Use Case**: Get comprehensive guidance for assessing and improving data quality

### Parameters
- `dataset_name` (str): Name of the dataset to assess for data quality

### Returns
- `str`: Data quality assessment guide with specific issues and recommendations

### Example Usage
```python
result = data_quality_assessment(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```
Let's systematically review the quality of your **sales** dataset.

📋 Dataset Overview:
• 1,500 rows × 8 columns
• Memory usage: 2.3 MB

🔍 Data Quality Indicators:

📋 Missing Values (2 columns affected):
🟡 email: 12.3% missing
🟢 phone: 8.7% missing

🎯 Recommended quality checks:
1. Comprehensive validation: `validate_data_quality('sales')`
2. Distribution analysis: Check for outliers and unusual patterns
3. Outlier detection: Find unusual values in numerical columns

💡 Quick quality assessment commands:
• `validate_data_quality('sales')` - Full quality report
• `detect_outliers('sales')` - Find unusual values
```

---

## find_datasources

**Category**: Prompt
**Purpose**: Discover available data files and present them as ready-to-load options
**Use Case**: Explore directories for data files and get specific load commands

### Parameters
- `directory_path` (str): Directory path to search for data files (defaults to current directory)

### Returns
- `str`: Data discovery report with specific load commands for found files

### Example Usage
```python
result = find_datasources(working_directory="/path/to/data", directory_path="./data")
print(result)
```

### Sample Output
```
📁 **Data Source Discovery: data**

Looking for data files in: `/path/to/data/data`

📊 Data files found in current directory:

• **sales_2023.csv** (CSV, 245.3 KB)
  → `load_dataset('sales_2023.csv', 'sales_2023')`

• **customer_data.json** (JSON, 89.7 KB)
  → `load_dataset('customer_data.json', 'customer_data')`

🚀 Ready to load data!

Found **2 data file(s)** ready for analysis.

Next steps:
1. Copy one of the `load_dataset()` commands above
2. Run it to load your data into memory
3. Start exploring with `dataset_first_look('dataset_name')`
```

---

## insight_generation_workshop

**Category**: Prompt
**Purpose**: Generate business insights from data analysis with contextual guidance
**Use Case**: Transform statistical findings into actionable business intelligence

### Parameters
- `dataset_name` (str): Name of the dataset to generate insights for
- `business_context` (str): Business context for analysis (e.g., 'sales', 'marketing', 'operations', 'hr')

### Returns
- `str`: Business insight generation framework with context-specific guidance

### Example Usage
```python
result = insight_generation_workshop(
    working_directory="/path/to/data",
    dataset_name="sales",
    business_context="sales"
)
print(result)
```

### Sample Output
```
💡 **Business Insights Workshop: sales**

Context: **sales** analysis

Let's transform your **1,500 records** into actionable business insights!

🎯 Insight generation framework:

Phase 1: Data Understanding
• What does each variable represent in your business?
• Which metrics matter most for decision-making?

Phase 2: Pattern Analysis
• `suggest_analysis('sales')` - Get AI-powered analysis recommendations
• Run suggested analyses to uncover patterns

🔍 Context-specific analysis for sales:
• Sales Performance: Analyze conversion rates, deal sizes, seasonal patterns
• Customer Behavior: Purchase frequency, preferences, lifetime value
• Channel Effectiveness: Performance by sales channel or region

🚀 Insight generation workflow:
1. Explore the data landscape
2. Run targeted analyses
3. Create compelling visualizations
4. Generate actionable recommendations
```

---

## list_analytics_assets

**Category**: Prompt
**Purpose**: Return comprehensive list of all Analytic Agent CLI capabilities
**Use Case**: Get complete reference of available functions, tools, and resources

### Parameters
None

### Returns
- `str`: Complete reference guide of all available analytics capabilities

### Example Usage
```python
result = list_analytics_assets(working_directory="/path/to/data")
print(result)
```

### Sample Output
```
# 🚀 Analytic Agent CLI Assets

## 📝 Prompts
Interactive conversation starters and analysis guides:
• dataset_first_look (dataset_name) - Initial exploration guide
• correlation_investigation (dataset_name) - Guide correlation analysis
• data_quality_assessment (dataset_name) - Systematic quality review

## 🔧 Tools
Data analysis and manipulation functions:
• load_dataset (file_path, dataset_name, sample_size) - Load datasets
• find_correlations (dataset_name, columns, threshold) - Find correlations
• segment_by_column (dataset_name, column_name) - Generic segmentation

## 📊 Resources
Dynamic data context and system information:
• analytics://current_dataset - Currently active dataset
• datasets://loaded - List of all loaded datasets
```

---

## pattern_discovery_session

**Category**: Prompt
**Purpose**: Open-ended pattern mining conversation with guided exploration framework
**Use Case**: Explore data for hidden patterns using multiple discovery techniques

### Parameters
- `dataset_name` (str): Name of the dataset to explore for patterns

### Returns
- `str`: Pattern discovery exploration guide with multiple discovery paths

### Example Usage
```python
result = pattern_discovery_session(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```
🔍 **Pattern Discovery Session: sales**

Let's uncover hidden patterns and insights in your data! With **1,500 records** and **8 variables**, there are many potential discoveries waiting.

📊 Your data landscape:
• 4 numerical variables: Perfect for trends, distributions, and correlations
• 3 categorical variables: Great for segmentation and group patterns
• 1 temporal variables: Ideal for time-based patterns and seasonality

🎯 Pattern discovery toolkit:

1. Distribution Patterns - Understand your data's shape
   • `analyze_distributions('sales', 'column_name')` - Detailed distribution analysis

2. Relationship Patterns - Find connections between variables
   • `find_correlations('sales')` - Statistical relationships
   • `create_chart('sales', 'scatter', 'revenue', 'marketing_spend')` - Visual relationships

🚀 Let's start discovering! Choose your exploration path:
1. "Show me the most interesting distributions"
2. "Find the strongest relationships"
3. "Reveal hidden segments"
```

---

## segmentation_workshop

**Category**: Prompt
**Purpose**: Interactive segmentation guidance based on actual dataset with strategic planning
**Use Case**: Plan and execute segmentation strategies based on available categorical variables

### Parameters
- `dataset_name` (str): Name of the dataset to plan segmentation for

### Returns
- `str`: Segmentation strategy guide with specific commands for available data

### Example Usage
```python
result = segmentation_workshop(working_directory="/path/to/data", dataset_name="sales")
print(result)
```

### Sample Output
```
Let's create meaningful segments from your **sales** data!

Available categorical columns for grouping:
• region: 4 unique values (examples: North, South, East, West)
• product: 12 unique values (examples: Product A, Product B, Product C)
• sales_rep: 8 unique values (examples: John Smith, Jane Doe, Mike Johnson)

📊 Numerical columns to analyze by segment:
• revenue: float64 (sample values: 15000, 22000, 18500)
• marketing_spend: float64 (sample values: 5000, 7500, 3200)

🎯 Segmentation strategies:
1. Simple segmentation: Group by one categorical column
   Example: `segment_by_column('sales', 'region')`

2. Cross-segmentation: Combine multiple categories
   Example: Group by region, then analyze patterns within each group

📈 Suggested analysis workflow:
1. Start with basic segmentation of your most important categorical variable
2. Look for interesting patterns in the numerical data
3. Create visualizations to show segment differences

Quick commands to try:
• `segment_by_column('sales', 'region')`
• `create_chart('sales', 'bar', 'region', 'revenue')`

Which segmentation approach interests you most?
```

---

## Summary

This comprehensive documentation covers all 39 analytics functions organized into three categories:

- **17 Tools**: Direct analysis functions for data manipulation, visualization, and advanced analytics
- **13 Resources**: Context and metadata functions for understanding dataset state and system capabilities  
- **9 Prompts**: Interactive guidance functions for analysis planning and workflow assistance

Each function includes detailed parameters, return values, realistic usage examples, and sample outputs to help users understand when and how to use each capability effectively.