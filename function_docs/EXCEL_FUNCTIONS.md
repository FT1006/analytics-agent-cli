# Excel Functions Reference

This document provides comprehensive documentation for all 16 Excel functions available in the Analytic Agent CLI.

## Overview

The Excel functions provide comprehensive spreadsheet manipulation capabilities including:
- Workbook creation and management
- Worksheet operations
- Data reading and writing
- Chart and table creation
- Cell formatting and formulas
- Range operations

---

## create_workbook

**Category**: Workbook operation
**Purpose**: Creates a new Excel workbook file with default worksheet
**Use Case**: When you need to start fresh with a new Excel file for data analysis or reporting

### Parameters
- `filepath` (str): Path to create the workbook file, relative to the working directory

### Returns
- `str`: Success message with created file path or error message

### Example Usage
```python
# Create a new workbook for sales data
result = create_workbook(working_directory="/path/to/data", filepath="sales_report_2024.xlsx")
print(result)
```

### Sample Output
```
"Created workbook at sales_report_2024.xlsx"
```

---

## get_workbook_metadata

**Category**: Workbook operation
**Purpose**: Retrieves metadata about an Excel workbook including sheets, size, and optionally used ranges
**Use Case**: When you need to understand the structure and content of an existing Excel file before processing

### Parameters
- `filepath` (str): Path to workbook file, relative to working directory
- `include_ranges` (bool, optional): Whether to include used ranges for each sheet (default: false)

### Returns
- `str`: JSON formatted metadata information or error message

### Example Usage
```python
# Get basic metadata about a workbook
result = get_workbook_metadata(working_directory="/path/to/data", filepath="financial_data.xlsx", include_ranges=True)
print(result)
```

### Sample Output
```json
{
  "filename": "financial_data.xlsx",
  "sheets": ["Q1_Data", "Q2_Data", "Summary"],
  "size": 45678,
  "modified": 1672531200.0,
  "used_ranges": {
    "Q1_Data": "A1:E100",
    "Q2_Data": "A1:E85",
    "Summary": "A1:C20"
  }
}
```

---

## create_worksheet

**Category**: Worksheet operation
**Purpose**: Creates a new worksheet in an existing Excel workbook
**Use Case**: When you need to add additional sheets to organize different types of data or analysis

### Parameters
- `filepath` (str): Path to workbook file, relative to working directory
- `sheet_name` (str): Name for the new worksheet

### Returns
- `str`: Success message confirming worksheet creation or error message

### Example Usage
```python
# Add a new worksheet for monthly analysis
result = create_worksheet(working_directory="/path/to/data", filepath="company_data.xlsx", sheet_name="March_Analysis")
print(result)
```

### Sample Output
```
"Created worksheet 'March_Analysis' in company_data.xlsx"
```

---

## copy_worksheet

**Category**: Worksheet operation
**Purpose**: Creates a copy of an existing worksheet within the same workbook
**Use Case**: When you want to duplicate a sheet structure or create templates for similar data

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `source_sheet` (str): Name of source worksheet to copy
- `target_sheet` (str): Name of target worksheet to create

### Returns
- `str`: Success message confirming worksheet copy or error message

### Example Usage
```python
# Copy a template sheet for a new month
result = copy_worksheet(working_directory="/path/to/data", filepath="monthly_reports.xlsx", source_sheet="Template", target_sheet="April_2024")
print(result)
```

### Sample Output
```
"Successfully copied sheet 'Template' to 'April_2024'"
```

---

## delete_worksheet

**Category**: Worksheet operation
**Purpose**: Removes a worksheet from an Excel workbook
**Use Case**: When you need to clean up obsolete sheets or remove test data from workbooks

### Parameters
- `filepath` (str): Path to workbook file, relative to working directory
- `sheet_name` (str): Name of the worksheet to delete

### Returns
- `str`: Success message confirming worksheet deletion or error message

### Example Usage
```python
# Remove an outdated worksheet
result = delete_worksheet(working_directory="/path/to/data", filepath="project_tracking.xlsx", sheet_name="Old_Data")
print(result)
```

### Sample Output
```
"Successfully deleted sheet 'Old_Data' from project_tracking.xlsx"
```

---

## rename_worksheet

**Category**: Worksheet operation
**Purpose**: Changes the name of an existing worksheet
**Use Case**: When you need to update sheet names for better organization or to reflect current data periods

### Parameters
- `filepath` (str): Path to workbook file, relative to working directory
- `old_name` (str): Current name of the worksheet to rename
- `new_name` (str): New name for the worksheet

### Returns
- `str`: Success message confirming worksheet rename or error message

### Example Usage
```python
# Rename a sheet to reflect current quarter
result = rename_worksheet(working_directory="/path/to/data", filepath="quarterly_results.xlsx", old_name="Current_Quarter", new_name="Q1_2024")
print(result)
```

### Sample Output
```
"Successfully renamed sheet from 'Current_Quarter' to 'Q1_2024' in quarterly_results.xlsx"
```

---

## read_data_from_excel

**Category**: Data operation
**Purpose**: Reads data from a specific range in an Excel worksheet
**Use Case**: When you need to extract data from Excel files for analysis, processing, or migration

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet to read from
- `start_cell` (str, optional): Starting cell (default "A1")
- `end_cell` (str, optional): Ending cell (auto-expands if not provided)

### Returns
- `str`: JSON formatted data with sheet information and cell contents

### Example Usage
```python
# Read sales data from a specific range
result = read_data_from_excel(working_directory="/path/to/data", filepath="sales_data.xlsx", sheet_name="Monthly_Sales", start_cell="A1", end_cell="D20")
print(result)
```

### Sample Output
```json
{
  "sheet_name": "Monthly_Sales",
  "range": "A1:D20",
  "data": [
    ["Product", "January", "February", "March"],
    ["Widget A", 1500, 1800, 2200],
    ["Widget B", 2300, 2100, 2500]
  ],
  "rows": 3,
  "columns": 4
}
```

---

## write_data_to_excel

**Category**: Data operation
**Purpose**: Writes structured data to a specific location in an Excel worksheet
**Use Case**: When you need to populate Excel sheets with processed data, analysis results, or imported information

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet to write to
- `data` (list): List of lists containing data to write (rows)
- `start_cell` (str, optional): Cell to start writing to (default "A1")

### Returns
- `str`: Success message with details about rows and cells written

### Example Usage
```python
# Write analysis results to Excel
data = [
    ["Category", "Total", "Average"],
    ["Sales", 15000, 2500],
    ["Marketing", 8000, 1333]
]
result = write_data_to_excel(working_directory="/path/to/data", filepath="results.xlsx", sheet_name="Summary", data=data, start_cell="B2")
print(result)
```

### Sample Output
```
"Successfully wrote 3 rows (9 cells) to sheet 'Summary' starting at B2"
```

---

## merge_cells

**Category**: Cell operation
**Purpose**: Merges a range of cells into a single cell
**Use Case**: When creating headers, titles, or formatted layouts that span multiple columns or rows

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet containing cells to merge
- `start_cell` (str): Top-left cell of range to merge (e.g., "A1")
- `end_cell` (str): Bottom-right cell of range to merge (e.g., "B2")

### Returns
- `str`: Success message confirming cell merge or error message

### Example Usage
```python
# Merge cells for a report title
result = merge_cells(working_directory="/path/to/data", filepath="report.xlsx", sheet_name="Dashboard", start_cell="A1", end_cell="E1")
print(result)
```

### Sample Output
```
"Range A1:E1 merged in sheet 'Dashboard'"
```

---

## unmerge_cells

**Category**: Cell operation
**Purpose**: Unmerges a previously merged range of cells
**Use Case**: When you need to separate merged cells to edit individual cell content or restructure layouts

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet containing cells to unmerge
- `start_cell` (str): Top-left cell of range to unmerge (e.g., "A1")
- `end_cell` (str): Bottom-right cell of range to unmerge (e.g., "B2")

### Returns
- `str`: Success message confirming cell unmerge or error message

### Example Usage
```python
# Unmerge title cells to edit individually
result = unmerge_cells(working_directory="/path/to/data", filepath="report.xlsx", sheet_name="Dashboard", start_cell="A1", end_cell="E1")
print(result)
```

### Sample Output
```
"Range A1:E1 unmerged successfully"
```

---

## apply_formula

**Category**: Cell operation
**Purpose**: Applies an Excel formula to a specific cell
**Use Case**: When you need to add calculations, references, or Excel functions to automate data processing

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet
- `cell` (str): Cell reference (e.g., "A1")
- `formula` (str): Excel formula to apply (with or without "=" prefix)

### Returns
- `str`: Success message confirming formula application or error message

### Example Usage
```python
# Apply a SUM formula to calculate totals
result = apply_formula(working_directory="/path/to/data", filepath="calculations.xlsx", sheet_name="Data", cell="D10", formula="=SUM(D1:D9)")
print(result)
```

### Sample Output
```
"Applied formula '=SUM(D1:D9)' to cell D10"
```

---

## format_range

**Category**: Range operation
**Purpose**: Applies comprehensive formatting to a range of cells including fonts, colors, borders, and alignment
**Use Case**: When you need to style Excel sheets for better readability, professional presentation, or data highlighting

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet
- `start_cell` (str): Starting cell reference (e.g., "A1")
- `end_cell` (str, optional): Ending cell reference (defaults to single cell)
- `bold` (bool, optional): Apply bold formatting
- `italic` (bool, optional): Apply italic formatting
- `underline` (bool, optional): Apply underline formatting
- `font_size` (int, optional): Font size in points
- `font_color` (str, optional): Font color in hex format (e.g., "FF0000" for red)
- `bg_color` (str, optional): Background color in hex format (e.g., "FFFF00" for yellow)
- `border_style` (str, optional): Border style ("thin", "thick", "medium", etc.)
- `border_color` (str, optional): Border color in hex format
- `number_format` (str, optional): Number format string (e.g., "0.00", "0%")
- `alignment` (str, optional): Text alignment ("left", "center", "right")
- `wrap_text` (bool, optional): Enable text wrapping
- `merge_cells` (bool, optional): Merge the specified range

### Returns
- `str`: Success message confirming range formatting or error message

### Example Usage
```python
# Format header row with bold, center alignment, and background color
result = format_range(working_directory="/path/to/data", filepath="styled_report.xlsx", sheet_name="Data", start_cell="A1", end_cell="E1", bold=True, bg_color="CCE5FF", alignment="center", border_style="thin")
print(result)
```

### Sample Output
```
"Range A1:E1 formatted successfully in sheet 'Data'"
```

---

## copy_range

**Category**: Range operation
**Purpose**: Copies a range of cells with values and formatting to another location
**Use Case**: When you need to duplicate data patterns, copy formatted sections, or replicate formulas across sheets

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of source worksheet
- `source_start` (str): Top-left cell of source range (e.g., "A1")
- `source_end` (str): Bottom-right cell of source range (e.g., "B2")
- `target_start` (str): Top-left cell where to paste (e.g., "D5")
- `target_sheet` (str, optional): Name of target worksheet (defaults to source sheet)

### Returns
- `str`: Success message with count of copied cells or error message

### Example Usage
```python
# Copy formatted header to another section
result = copy_range(working_directory="/path/to/data", filepath="template.xlsx", sheet_name="Source", source_start="A1", source_end="C3", target_start="F1", target_sheet="Destination")
print(result)
```

### Sample Output
```
"Range copied successfully (9 cells) from sheet 'Source' to sheet 'Destination'"
```

---

## delete_range

**Category**: Range operation
**Purpose**: Deletes a range of cells and shifts remaining cells up or left
**Use Case**: When you need to remove data ranges and reorganize spreadsheet layout automatically

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet containing cells to delete
- `start_cell` (str): Top-left cell of range to delete (e.g., "A1")
- `end_cell` (str): Bottom-right cell of range to delete (e.g., "B2")
- `shift_direction` (str, optional): Direction to shift cells after deletion ("up" or "left", default "up")

### Returns
- `str`: Success message confirming range deletion or error message

### Example Usage
```python
# Delete obsolete data rows and shift remaining data up
result = delete_range(working_directory="/path/to/data", filepath="cleanup.xlsx", sheet_name="Data", start_cell="A5", end_cell="E10", shift_direction="up")
print(result)
```

### Sample Output
```
"Range A5:E10 deleted successfully"
```

---

## create_chart_excel

**Category**: Chart operation
**Purpose**: Creates and embeds various types of charts in Excel worksheets using cell ranges
**Use Case**: When you need to visualize data with professional charts for reports, dashboards, or presentations

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet
- `data_range` (str): Cell range for chart data (e.g., "A1:B10")
- `chart_type` (str): Type of chart ("column", "bar", "line", "pie", "area", "scatter")
- `target_cell` (str): Cell where chart will be placed (e.g., "D2")
- `title` (str, optional): Chart title

### Returns
- `str`: Success message confirming chart creation or error message

### Example Usage
```python
# Create a column chart showing monthly sales
result = create_chart_excel(working_directory="/path/to/data", filepath="sales_analysis.xlsx", sheet_name="Monthly_Data", data_range="A1:B13", chart_type="column", target_cell="D2", title="Monthly Sales Trend")
print(result)
```

### Sample Output
```
"Chart 'column' created successfully in sheet 'Monthly_Data' at D2"
```

---

## create_table

**Category**: Table operation
**Purpose**: Creates a native Excel table from a specified range of data with automatic filtering and formatting
**Use Case**: When you need to create structured, filterable data tables with built-in Excel table features

### Parameters
- `filepath` (str): Path to Excel file, relative to working directory
- `sheet_name` (str): Name of worksheet
- `table_name` (str): Name for the table
- `data_range` (str): Cell range for the table (e.g., "A1:C10")

### Returns
- `str`: Success message confirming table creation or error message

### Example Usage
```python
# Create a table for employee data with automatic filtering
result = create_table(working_directory="/path/to/data", filepath="hr_data.xlsx", sheet_name="Employees", table_name="EmployeeTable", data_range="A1:F25")
print(result)
```

### Sample Output
```
"Table 'EmployeeTable' created successfully in sheet 'Employees' with range A1:F25"
```

---

## Function Categories Summary

### Workbook Operations (2 functions)
- `create_workbook`: Create new Excel files
- `get_workbook_metadata`: Analyze existing files

### Worksheet Operations (4 functions)
- `create_worksheet`: Add new sheets
- `copy_worksheet`: Duplicate sheet structures
- `delete_worksheet`: Remove unnecessary sheets
- `rename_worksheet`: Update sheet names

### Data Operations (2 functions)
- `read_data_from_excel`: Extract data from Excel
- `write_data_to_excel`: Insert data into Excel

### Cell Operations (3 functions)
- `merge_cells`: Combine cells for headers/titles
- `unmerge_cells`: Separate merged cells
- `apply_formula`: Add calculations and functions

### Range Operations (3 functions)
- `format_range`: Style and format cell ranges
- `copy_range`: Duplicate data with formatting
- `delete_range`: Remove data ranges with shifting

### Advanced Features (2 functions)
- `create_chart_excel`: Generate visual charts
- `create_table`: Create structured Excel tables

## Common Usage Patterns

### Data Import/Export Workflow
1. Use `create_workbook` to start fresh
2. Use `write_data_to_excel` to populate data
3. Use `format_range` for professional presentation
4. Use `create_chart_excel` for visualization

### Data Analysis Setup
1. Use `get_workbook_metadata` to understand existing data
2. Use `read_data_from_excel` to extract specific ranges
3. Use `create_worksheet` for analysis results
4. Use `apply_formula` for calculations

### Report Generation
1. Use `copy_worksheet` to duplicate templates
2. Use `write_data_to_excel` for current data
3. Use `format_range` for styling
4. Use `merge_cells` for headers and titles
5. Use `create_table` for structured data presentation

## Best Practices

1. **File Security**: All functions validate file paths within the working directory
2. **Error Handling**: Functions return descriptive error messages for troubleshooting
3. **Range Validation**: Cell references are validated before operations
4. **Formula Safety**: Unsafe Excel functions are blocked in formula validation
5. **Resource Management**: Workbooks are properly closed after operations
6. **Data Integrity**: Functions check for existing data before destructive operations

## Dependencies

All Excel functions require the `openpyxl` library. If not available, functions will return an error message with installation instructions: `pip install openpyxl`