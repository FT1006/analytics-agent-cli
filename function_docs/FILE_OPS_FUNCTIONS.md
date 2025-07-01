# File Operations Functions Reference

This document provides comprehensive documentation for all 5 file operation functions available in the Analytic Agent CLI.

## Overview

The file operations functions provide essential file system interactions for secure data analysis workflows. All functions include security controls to prevent access outside the designated working directory.

**Security Features:**
- Path traversal protection (prevents "../" attacks)
- Working directory containment
- File type validation (where applicable)
- Error handling with descriptive messages

---

## get_working_directory

**Category**: File System
**Purpose**: Returns the absolute path of the current working directory
**Use Case**: Essential first step in any file operation session to establish the workspace context

### Parameters
- No parameters required (working_directory is provided automatically by Staffer)

### Returns
- `str`: Absolute path to the working directory

### Example Usage
```python
# Must be called at session start
result = get_working_directory(working_directory="/Users/analyst/data")
print(result)
```

### Sample Output
```
/Users/analyst/data
```

---

## get_files_info

**Category**: File System
**Purpose**: Lists files and directories with metadata including size and type information
**Use Case**: Exploring directory structure, checking file sizes before operations, understanding workspace layout

### Parameters
- `directory` (str, optional): Relative path to directory to list. If not provided, lists the working directory

### Returns
- `str`: Formatted list of files with metadata, or error message

### Example Usage
```python
# List files in working directory
result = get_files_info(working_directory="/Users/analyst/data")
print(result)

# List files in specific subdirectory
result = get_files_info(working_directory="/Users/analyst/data", directory="datasets")
print(result)
```

### Sample Output
```
- sales_data.csv: file_size=1024576 bytes, is_dir=False
- quarterly_reports: file_size=4096 bytes, is_dir=True
- analysis.py: file_size=2048 bytes, is_dir=False
- temp_files: file_size=4096 bytes, is_dir=True
```

---

## get_file_content

**Category**: Content
**Purpose**: Reads and returns the content of a text file with size limitations for safety
**Use Case**: Reading configuration files, data files, scripts, or any text-based content for analysis

### Parameters
- `file_path` (str): Relative path to the file to read

### Returns
- `str`: File content (up to 10,000 characters) or error message

### Example Usage
```python
# Read a CSV file
result = get_file_content(working_directory="/Users/analyst/data", file_path="sales_data.csv")
print(result)

# Read a Python script
result = get_file_content(working_directory="/Users/analyst/data", file_path="analysis.py")
print(result)

# Read configuration file
result = get_file_content(working_directory="/Users/analyst/data", file_path="config.json")
print(result)
```

### Sample Output
```
Date,Product,Sales,Region
2024-01-01,Widget A,1500,North
2024-01-01,Widget B,2300,South
2024-01-02,Widget A,1200,North
...File "sales_data.csv" truncated at 10000 characters
```

**Security Considerations:**
- Maximum 10,000 characters to prevent memory issues
- Only reads files within working directory
- Handles binary files gracefully with error messages

---

## write_file

**Category**: Content
**Purpose**: Creates or overwrites files with specified content, automatically creating directories if needed
**Use Case**: Saving analysis results, creating configuration files, generating reports, storing processed data

### Parameters
- `file_path` (str): Relative path where to write the file
- `content` (str): Content to write to the file

### Returns
- `str`: Success message with character count, or error message

### Example Usage
```python
# Write analysis results
result = write_file(
    working_directory="/Users/analyst/data",
    file_path="results/analysis_summary.txt",
    content="Analysis completed. Total sales: $45,000"
)
print(result)

# Write CSV data
csv_content = "Name,Value\nItem1,100\nItem2,200"
result = write_file(
    working_directory="/Users/analyst/data",
    file_path="output/processed_data.csv",
    content=csv_content
)
print(result)

# Write Python script
script_content = """import pandas as pd
df = pd.read_csv('input.csv')
print(df.head())"""
result = write_file(
    working_directory="/Users/analyst/data",
    file_path="scripts/data_preview.py",
    content=script_content
)
print(result)
```

### Sample Output
```
Successfully wrote to "results/analysis_summary.txt" (35 characters written)
```

**Security Considerations:**
- Automatically creates parent directories if they don't exist
- Overwrites existing files without warning
- Cannot write outside working directory
- No file size limits (use responsibly)

---

## run_python_file

**Category**: Execution
**Purpose**: Executes Python scripts within the working directory with timeout protection
**Use Case**: Running data analysis scripts, executing automated workflows, testing Python code

### Parameters
- `file_path` (str): Relative path to the Python file to execute

### Returns
- `str`: Combined STDOUT and STDERR output, or error message

### Example Usage
```python
# Run a data analysis script
result = run_python_file(working_directory="/Users/analyst/data", file_path="analysis.py")
print(result)

# Run a data processing script
result = run_python_file(working_directory="/Users/analyst/data", file_path="scripts/process_sales.py")
print(result)

# Run a quick calculation
result = run_python_file(working_directory="/Users/analyst/data", file_path="quick_calc.py")
print(result)
```

### Sample Output
```
STDOUT:    Product  Sales
0  Widget A   1500
1  Widget B   2300
2  Widget C    980
Total Sales: $4780

STDERR: 
```

**Security Considerations:**
- 30-second timeout to prevent runaway processes
- Only executes .py files
- Cannot execute files outside working directory
- Captures both output and errors
- Returns exit code information for failed executions

**Common Use Cases:**
- Data validation scripts
- ETL pipeline components
- Statistical analysis automation
- Report generation
- Data quality checks

---

## Function Integration Patterns

### Typical Workflow
1. **Initialize**: `get_working_directory()` to establish context
2. **Explore**: `get_files_info()` to understand available data
3. **Read**: `get_file_content()` to examine input files
4. **Process**: `run_python_file()` to execute analysis
5. **Save**: `write_file()` to store results

### Error Handling
All functions return descriptive error messages for common scenarios:
- Path traversal attempts
- Missing files/directories
- Permission issues
- File type mismatches
- Execution timeouts

### Best Practices
- Always call `get_working_directory()` first
- Use `get_files_info()` before file operations
- Check file content before processing large files
- Save intermediate results with `write_file()`
- Use descriptive file paths and names