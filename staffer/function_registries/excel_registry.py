"""Excel operations function registry for Staffer."""

from google.genai import types

# Import Excel workbook functions and schemas
from ..functions.excel.workbooks.create_workbook import schema_create_workbook, create_workbook
from ..functions.excel.workbooks.get_workbook_metadata import schema_get_workbook_metadata, get_workbook_metadata

# Import Excel worksheet functions and schemas
from ..functions.excel.worksheets.create_worksheet import schema_create_worksheet, create_worksheet
from ..functions.excel.worksheets.rename_worksheet import schema_rename_worksheet, rename_worksheet
from ..functions.excel.worksheets.delete_worksheet import schema_delete_worksheet, delete_worksheet
from ..functions.excel.worksheets.read_data_from_excel import schema_read_data_from_excel, read_data_from_excel
from ..functions.excel.worksheets.write_data_to_excel import schema_write_data_to_excel, write_data_to_excel
from ..functions.excel.worksheets.copy_worksheet import schema_copy_worksheet, copy_worksheet

# Import Excel cells/ranges functions and schemas
from ..functions.excel.cells_ranges.validate_excel_range import schema_validate_excel_range, validate_excel_range
from ..functions.excel.cells_ranges.merge_cells import schema_merge_cells, merge_cells
from ..functions.excel.cells_ranges.unmerge_cells import schema_unmerge_cells, unmerge_cells
from ..functions.excel.cells_ranges.copy_range import schema_copy_range, copy_range
from ..functions.excel.cells_ranges.delete_range import schema_delete_range, delete_range
from ..functions.excel.cells_ranges.validate_formula_syntax import schema_validate_formula_syntax, validate_formula_syntax
from ..functions.excel.cells_ranges.apply_formula import schema_apply_formula, apply_formula
from ..functions.excel.cells_ranges.get_data_validation_info import schema_get_data_validation_info, get_data_validation_info
from ..functions.excel.cells_ranges.format_range import schema_format_range, format_range

# Import Excel charts/tables functions and schemas
from ..functions.excel.charts_tables.create_table import schema_create_table, create_table
from ..functions.excel.charts_tables.create_chart import schema_create_chart as schema_create_chart_excel, create_chart as create_chart_excel
from ..functions.excel.charts_tables.create_pivot_table import schema_create_pivot_table, create_pivot_table

# Excel operations schemas list
excel_schemas = [
    # Workbooks
    schema_create_workbook,
    schema_get_workbook_metadata,
    # Worksheets
    schema_create_worksheet,
    schema_rename_worksheet,
    schema_delete_worksheet,
    schema_read_data_from_excel,
    schema_write_data_to_excel,
    schema_copy_worksheet,
    # Cells/Ranges
    schema_validate_excel_range,
    schema_merge_cells,
    schema_unmerge_cells,
    schema_copy_range,
    schema_delete_range,
    schema_validate_formula_syntax,
    schema_apply_formula,
    schema_get_data_validation_info,
    schema_format_range,
    # Charts/Tables
    schema_create_table,
    schema_create_chart_excel,
    schema_create_pivot_table,
]

# Excel operations function mapping
excel_functions = {
    # Workbooks
    "create_workbook": create_workbook,
    "get_workbook_metadata": get_workbook_metadata,
    # Worksheets
    "create_worksheet": create_worksheet,
    "rename_worksheet": rename_worksheet,
    "delete_worksheet": delete_worksheet,
    "read_data_from_excel": read_data_from_excel,
    "write_data_to_excel": write_data_to_excel,
    "copy_worksheet": copy_worksheet,
    # Cells/Ranges
    "validate_excel_range": validate_excel_range,
    "merge_cells": merge_cells,
    "unmerge_cells": unmerge_cells,
    "copy_range": copy_range,
    "delete_range": delete_range,
    "validate_formula_syntax": validate_formula_syntax,
    "apply_formula": apply_formula,
    "get_data_validation_info": get_data_validation_info,
    "format_range": format_range,
    # Charts/Tables
    "create_table": create_table,
    "create_chart_excel": create_chart_excel,
    "create_pivot_table": create_pivot_table,
}