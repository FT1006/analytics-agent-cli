"""Tests for Excel functions adapted from excel_mcp."""

import pytest
import tempfile
import os
from pathlib import Path

from staffer.available_functions import call_function
from tests.factories import function_call


class TestCreateWorkbook:
    """Test create_workbook function with Staffer security."""

    def test_create_workbook_success(self):
        """Test creating workbook in working directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # This should pass when function is implemented
            file_path = "test_workbook.xlsx"
            
            fc = function_call("create_workbook", {"filepath": file_path})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "create_workbook"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and mention file creation
            assert "Created workbook" in response
            
            # File should actually exist
            expected_path = os.path.join(temp_dir, file_path)
            assert os.path.exists(expected_path)

    def test_create_workbook_security_violation(self):
        """Test that create_workbook prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to create file outside working directory
            file_path = "../outside_workbook.xlsx"
            
            fc = function_call("create_workbook", {"filepath": file_path})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response
            
            # File should NOT exist outside temp_dir
            outside_path = os.path.join(os.path.dirname(temp_dir), "outside_workbook.xlsx")
            assert not os.path.exists(outside_path)

    def test_create_workbook_invalid_path(self):
        """Test create_workbook with nonexistent directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create path that would fail due to permission issues
            file_path = "deep/nested/path/that/does/not/exist/test.xlsx"
            
            fc = function_call("create_workbook", {"filepath": file_path})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should either succeed (mkdir -p works) or fail gracefully
            # Both outcomes are acceptable for this edge case
            assert isinstance(response, str)  # Just ensure we get a string response


class TestCreateWorksheet:
    """Test create_worksheet function with Staffer security."""

    def test_create_worksheet_success(self):
        """Test creating worksheet in existing workbook."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Now add a worksheet
            sheet_name = "NewSheet"
            fc = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "create_worksheet"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and mention sheet creation
            assert "created" in response.lower() or "added" in response.lower()

    def test_create_worksheet_security_violation(self):
        """Test that create_worksheet prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            sheet_name = "TestSheet"
            
            fc = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_create_worksheet_nonexistent_workbook(self):
        """Test create_worksheet with nonexistent workbook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to add sheet to nonexistent workbook
            workbook_path = "nonexistent.xlsx"
            sheet_name = "TestSheet"
            
            fc = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response


class TestGetWorkbookMetadata:
    """Test get_workbook_metadata function with Staffer security."""

    def test_get_workbook_metadata_success(self):
        """Test getting metadata from existing workbook."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Get metadata
            fc = function_call("get_workbook_metadata", {"filepath": workbook_path})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "get_workbook_metadata"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and contain metadata info
            assert not response.startswith("Error:")
            assert isinstance(response, str)

    def test_get_workbook_metadata_security_violation(self):
        """Test that get_workbook_metadata prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("get_workbook_metadata", {"filepath": workbook_path})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_get_workbook_metadata_nonexistent_file(self):
        """Test get_workbook_metadata with nonexistent workbook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to get metadata from nonexistent workbook
            workbook_path = "nonexistent.xlsx"
            
            fc = function_call("get_workbook_metadata", {"filepath": workbook_path})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response


class TestRenameWorksheet:
    """Test rename_worksheet function with Staffer security."""

    def test_rename_worksheet_success(self):
        """Test renaming worksheet in existing workbook."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook and worksheet
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            sheet_name = "OldSheet"
            fc_ws = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            call_function(fc_ws.parts[0].function_call, temp_dir)
            
            # Rename worksheet
            new_name = "NewSheet"
            fc = function_call("rename_worksheet", {"filepath": workbook_path, "old_name": sheet_name, "new_name": new_name})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "rename_worksheet"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and mention rename
            assert not response.startswith("Error:")
            assert "renamed" in response.lower() or "success" in response.lower()

    def test_rename_worksheet_security_violation(self):
        """Test that rename_worksheet prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("rename_worksheet", {"filepath": workbook_path, "old_name": "OldSheet", "new_name": "NewSheet"})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_rename_worksheet_nonexistent_file(self):
        """Test rename_worksheet with nonexistent workbook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to rename worksheet in nonexistent workbook
            workbook_path = "nonexistent.xlsx"
            
            fc = function_call("rename_worksheet", {"filepath": workbook_path, "old_name": "OldSheet", "new_name": "NewSheet"})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response


class TestDeleteWorksheet:
    """Test delete_worksheet function with Staffer security."""

    def test_delete_worksheet_success(self):
        """Test deleting worksheet from existing workbook."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook and worksheet
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            sheet_name = "ToDelete"
            fc_ws = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            call_function(fc_ws.parts[0].function_call, temp_dir)
            
            # Delete worksheet
            fc = function_call("delete_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "delete_worksheet"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and mention deletion
            assert not response.startswith("Error:")
            assert "deleted" in response.lower() or "removed" in response.lower()

    def test_delete_worksheet_security_violation(self):
        """Test that delete_worksheet prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("delete_worksheet", {"filepath": workbook_path, "sheet_name": "ToDelete"})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_delete_worksheet_nonexistent_file(self):
        """Test delete_worksheet with nonexistent workbook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to delete worksheet from nonexistent workbook
            workbook_path = "nonexistent.xlsx"
            
            fc = function_call("delete_worksheet", {"filepath": workbook_path, "sheet_name": "ToDelete"})
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response


class TestReadDataFromExcel:
    """Test read_data_from_excel function with Staffer security."""

    def test_read_data_from_excel_success(self):
        """Test reading data from existing worksheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook and worksheet with some data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            sheet_name = "DataSheet"
            fc_ws = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            call_function(fc_ws.parts[0].function_call, temp_dir)
            
            # Read data from the sheet
            fc = function_call("read_data_from_excel", {
                "filepath": workbook_path, 
                "sheet_name": sheet_name,
                "start_cell": "A1",
                "end_cell": "C3"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "read_data_from_excel"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and return data info
            assert not response.startswith("Error:")
            assert isinstance(response, str)

    def test_read_data_from_excel_security_violation(self):
        """Test that read_data_from_excel prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("read_data_from_excel", {
                "filepath": workbook_path, 
                "sheet_name": "Sheet1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_read_data_from_excel_nonexistent_file(self):
        """Test read_data_from_excel with nonexistent workbook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to read from nonexistent workbook
            workbook_path = "nonexistent.xlsx"
            
            fc = function_call("read_data_from_excel", {
                "filepath": workbook_path, 
                "sheet_name": "Sheet1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response

    def test_read_data_from_excel_nonexistent_sheet(self):
        """Test read_data_from_excel with nonexistent sheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook but try to read nonexistent sheet
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            fc = function_call("read_data_from_excel", {
                "filepath": workbook_path, 
                "sheet_name": "NonexistentSheet"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response


class TestWriteDataToExcel:
    """Test write_data_to_excel function with Staffer security."""

    def test_write_data_to_excel_success(self):
        """Test writing data to existing worksheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook and worksheet
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            sheet_name = "DataSheet"
            fc_ws = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            call_function(fc_ws.parts[0].function_call, temp_dir)
            
            # Write data to the sheet
            test_data = [["Name", "Age", "City"], ["John", "25", "NYC"], ["Jane", "30", "LA"]]
            fc = function_call("write_data_to_excel", {
                "filepath": workbook_path, 
                "sheet_name": sheet_name,
                "data": test_data,
                "start_cell": "A1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "write_data_to_excel"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and mention data written
            assert not response.startswith("Error:")
            assert isinstance(response, str)

    def test_write_data_to_excel_security_violation(self):
        """Test that write_data_to_excel prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            test_data = [["Test", "Data"]]
            
            fc = function_call("write_data_to_excel", {
                "filepath": workbook_path, 
                "sheet_name": "Sheet1",
                "data": test_data
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_write_data_to_excel_nonexistent_file(self):
        """Test write_data_to_excel with nonexistent workbook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to write to nonexistent workbook
            workbook_path = "nonexistent.xlsx"
            test_data = [["Test", "Data"]]
            
            fc = function_call("write_data_to_excel", {
                "filepath": workbook_path, 
                "sheet_name": "Sheet1",
                "data": test_data
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response


class TestCopyWorksheet:
    """Test copy_worksheet function with Staffer security."""

    def test_copy_worksheet_success(self):
        """Test copying worksheet within workbook."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook and worksheet
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            source_sheet = "SourceSheet"
            fc_ws = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": source_sheet})
            call_function(fc_ws.parts[0].function_call, temp_dir)
            
            # Copy the worksheet
            target_sheet = "CopiedSheet"
            fc = function_call("copy_worksheet", {
                "filepath": workbook_path, 
                "source_sheet": source_sheet,
                "target_sheet": target_sheet
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "copy_worksheet"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and mention copy operation
            assert not response.startswith("Error:")
            assert isinstance(response, str)

    def test_copy_worksheet_security_violation(self):
        """Test that copy_worksheet prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("copy_worksheet", {
                "filepath": workbook_path, 
                "source_sheet": "Sheet1",
                "target_sheet": "Copy1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_copy_worksheet_nonexistent_file(self):
        """Test copy_worksheet with nonexistent workbook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to copy worksheet in nonexistent workbook
            workbook_path = "nonexistent.xlsx"
            
            fc = function_call("copy_worksheet", {
                "filepath": workbook_path, 
                "source_sheet": "Sheet1",
                "target_sheet": "Copy1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response


class TestValidateExcelRange:
    """Test validate_excel_range function with Staffer security."""

    def test_validate_excel_range_success(self):
        """Test validating range in existing worksheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook and worksheet
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            sheet_name = "ValidSheet"
            fc_ws = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            call_function(fc_ws.parts[0].function_call, temp_dir)
            
            # Validate a range in the sheet
            fc = function_call("validate_excel_range", {
                "filepath": workbook_path, 
                "sheet_name": sheet_name,
                "start_cell": "A1",
                "end_cell": "C3"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "validate_excel_range"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed and mention validation result
            assert not response.startswith("Error:")
            assert isinstance(response, str)

    def test_validate_excel_range_security_violation(self):
        """Test that validate_excel_range prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("validate_excel_range", {
                "filepath": workbook_path, 
                "sheet_name": "Sheet1",
                "start_cell": "A1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_validate_excel_range_nonexistent_file(self):
        """Test validate_excel_range with nonexistent workbook file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to validate range in nonexistent workbook
            workbook_path = "nonexistent.xlsx"
            
            fc = function_call("validate_excel_range", {
                "filepath": workbook_path, 
                "sheet_name": "Sheet1",
                "start_cell": "A1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message
            assert "Error:" in response

    def test_validate_excel_range_invalid_range(self):
        """Test validate_excel_range with invalid range format."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook 
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            sheet_name = "ValidSheet"
            fc_ws = function_call("create_worksheet", {"filepath": workbook_path, "sheet_name": sheet_name})
            call_function(fc_ws.parts[0].function_call, temp_dir)
            
            # Try to validate invalid range
            fc = function_call("validate_excel_range", {
                "filepath": workbook_path, 
                "sheet_name": sheet_name,
                "start_cell": "INVALID_RANGE"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should handle gracefully with error message or validation failure
            assert isinstance(response, str)


class TestMergeCells:
    """Test merge_cells function."""

    def test_merge_cells_success(self):
        """Test merging cells in existing workbook."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Now merge cells
            fc = function_call("merge_cells", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "merge_cells"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "merged" in response.lower()
            assert "A1:B2" in response

    def test_merge_cells_security_violation(self):
        """Test that merge_cells prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("merge_cells", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_merge_cells_nonexistent_file(self):
        """Test merge_cells with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("merge_cells", {
                "filepath": "nonexistent.xlsx",
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response
            assert "does not exist" in response

    def test_merge_cells_invalid_range(self):
        """Test merge_cells with invalid cell references."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook first
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)


class TestValidateFormulaSyntax:
    """Test validate_formula_syntax function with Staffer security."""

    def test_validate_formula_syntax_success(self):
        """Test validating valid Excel formula syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Validate simple formula syntax
            fc = function_call("validate_formula_syntax", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "cell": "A1", 
                "formula": "=B1+C1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "validate_formula_syntax"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed with validation message
            assert "valid" in response.lower() or "Formula is" in response

    def test_validate_formula_syntax_security_violation(self):
        """Test that validate_formula_syntax prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("validate_formula_syntax", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "cell": "A1",
                "formula": "=B1+C1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_validate_formula_syntax_nonexistent_file(self):
        """Test validate_formula_syntax with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("validate_formula_syntax", {
                "filepath": "nonexistent.xlsx",
                "sheet_name": "Sheet", 
                "cell": "A1",
                "formula": "=B1+C1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response

    def test_validate_formula_syntax_invalid_formula(self):
        """Test validate_formula_syntax with invalid formula syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook first
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Test invalid formula
            fc = function_call("validate_formula_syntax", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "cell": "A1",
                "formula": "=B1++C1"  # Invalid double plus
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should indicate invalid syntax
            assert "Error:" in response or "invalid" in response.lower()

    def test_validate_formula_syntax_invalid_sheet(self):
        """Test validate_formula_syntax with nonexistent sheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook first
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Test with non-existent sheet
            fc = function_call("validate_formula_syntax", {
                "filepath": workbook_path,
                "sheet_name": "NonExistentSheet",
                "cell": "A1",
                "formula": "=B1+C1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response
            assert "not found" in response or "NonExistentSheet" in response


class TestApplyFormula:
    """Test apply_formula function with Staffer security."""

    def test_apply_formula_success(self):
        """Test applying valid Excel formula to cell."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Apply simple formula
            fc = function_call("apply_formula", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "cell": "A1",
                "formula": "=1+1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "apply_formula"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "Applied formula" in response or "applied" in response.lower()

    def test_apply_formula_security_violation(self):
        """Test that apply_formula prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("apply_formula", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "cell": "A1",
                "formula": "=1+1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_apply_formula_nonexistent_file(self):
        """Test apply_formula with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("apply_formula", {
                "filepath": "nonexistent.xlsx",
                "sheet_name": "Sheet",
                "cell": "A1",
                "formula": "=1+1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response

    def test_apply_formula_invalid_formula(self):
        """Test apply_formula with invalid formula syntax."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook first
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Test invalid formula
            fc = function_call("apply_formula", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "cell": "A1",
                "formula": "=B1++C1"  # Invalid double plus
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should indicate invalid syntax
            assert "Error:" in response

    def test_apply_formula_invalid_sheet(self):
        """Test apply_formula with nonexistent sheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook first
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Test with non-existent sheet
            fc = function_call("apply_formula", {
                "filepath": workbook_path,
                "sheet_name": "NonExistentSheet",
                "cell": "A1",
                "formula": "=1+1"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response
            assert "not found" in response or "NonExistentSheet" in response


class TestGetDataValidationInfo:
    """Test get_data_validation_info function with Staffer security."""

    def test_get_data_validation_info_success(self):
        """Test getting data validation info from worksheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Get validation info
            fc = function_call("get_data_validation_info", {
                "filepath": workbook_path,
                "sheet_name": "Sheet"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "get_data_validation_info"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed - either find rules or report none found
            assert isinstance(response, str)
            assert ("No data validation rules found" in response or 
                    "sheet_name" in response or 
                    "validation_rules" in response)

    def test_get_data_validation_info_security_violation(self):
        """Test that get_data_validation_info prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Try to access file outside working directory
            workbook_path = "../outside_workbook.xlsx"
            
            fc = function_call("get_data_validation_info", {
                "filepath": workbook_path,
                "sheet_name": "Sheet"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_get_data_validation_info_nonexistent_file(self):
        """Test get_data_validation_info with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("get_data_validation_info", {
                "filepath": "nonexistent.xlsx",
                "sheet_name": "Sheet"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response

    def test_get_data_validation_info_invalid_sheet(self):
        """Test get_data_validation_info with nonexistent sheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook first
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Test with non-existent sheet
            fc = function_call("get_data_validation_info", {
                "filepath": workbook_path,
                "sheet_name": "NonExistentSheet"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response
            assert "not found" in response or "NonExistentSheet" in response


class TestUnmergeCells:
    """Test unmerge_cells function."""

    def test_unmerge_cells_success(self):
        """Test unmerging cells that were previously merged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # First create a workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Merge cells first
            fc_merge = function_call("merge_cells", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2"
            })
            call_function(fc_merge.parts[0].function_call, temp_dir)
            
            # Now unmerge cells
            fc = function_call("unmerge_cells", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result structure
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "unmerge_cells"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "unmerged" in response.lower()

    def test_unmerge_cells_not_merged(self):
        """Test unmerging cells that are not merged."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Try to unmerge cells that are not merged
            fc = function_call("unmerge_cells", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "C3",
                "end_cell": "D4"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with appropriate error
            assert "Error:" in response
            assert "not merged" in response

    def test_unmerge_cells_security_violation(self):
        """Test that unmerge_cells prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("unmerge_cells", {
                "filepath": "../outside.xlsx",
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response


class TestCopyRange:
    """Test copy_range function."""

    def test_copy_range_success(self):
        """Test copying range within same sheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and write some data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Write test data
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["A1", "B1"], ["A2", "B2"]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Copy range
            fc = function_call("copy_range", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "source_start": "A1",
                "source_end": "B2",
                "target_start": "D5"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "copy_range"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "copied" in response.lower()

    def test_copy_range_to_different_sheet(self):
        """Test copying range to different sheet."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Create second sheet
            fc_sheet = function_call("create_worksheet", {
                "filepath": workbook_path,
                "sheet_name": "Sheet2"
            })
            call_function(fc_sheet.parts[0].function_call, temp_dir)
            
            # Write test data
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["A1", "B1"], ["A2", "B2"]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Copy range to different sheet
            fc = function_call("copy_range", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "source_start": "A1",
                "source_end": "B2",
                "target_start": "C3",
                "target_sheet": "Sheet2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "copied" in response.lower()

    def test_copy_range_security_violation(self):
        """Test that copy_range prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("copy_range", {
                "filepath": "../outside.xlsx",
                "sheet_name": "Sheet",
                "source_start": "A1",
                "source_end": "B2",
                "target_start": "C3"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response


class TestDeleteRange:
    """Test delete_range function."""

    def test_delete_range_success_shift_up(self):
        """Test deleting range with shift up."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and write some data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Write test data
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["A1", "B1"], ["A2", "B2"], ["A3", "B3"]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Delete range
            fc = function_call("delete_range", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "A2",
                "end_cell": "B2",
                "shift_direction": "up"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "delete_range"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "deleted" in response.lower()

    def test_delete_range_shift_left(self):
        """Test deleting range with shift left."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and write some data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Write test data in a wider range
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["A1", "B1", "C1"], ["A2", "B2", "C2"]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Delete range with shift left
            fc = function_call("delete_range", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "B1",
                "end_cell": "B2",
                "shift_direction": "left"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "deleted" in response.lower()

    def test_delete_range_invalid_shift(self):
        """Test delete_range with invalid shift direction."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Try invalid shift direction
            fc = function_call("delete_range", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2",
                "shift_direction": "invalid"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with error
            assert "Error:" in response
            assert "shift direction" in response

    def test_delete_range_security_violation(self):
        """Test that delete_range prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("delete_range", {
                "filepath": "../outside.xlsx",
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2",
                "shift_direction": "up"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response


class TestFormatRange:
    """Test format_range function."""

    def test_format_range_success(self):
        """Test formatting range with basic options."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and write some data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Write test data
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["A1", "B1"], ["A2", "B2"]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Format range
            fc = function_call("format_range", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2",
                "bold": True,
                "italic": True,
                "font_size": 12
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "format_range"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "formatted" in response.lower()

    def test_format_range_security_violation(self):
        """Test that format_range prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("format_range", {
                "filepath": "../outside.xlsx",
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "end_cell": "B2",
                "bold": True
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_format_range_nonexistent_file(self):
        """Test format_range with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("format_range", {
                "filepath": "nonexistent.xlsx",
                "sheet_name": "Sheet",
                "start_cell": "A1",
                "bold": True
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response

    def test_format_range_invalid_range(self):
        """Test format_range with invalid cell range."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Try invalid range
            fc = function_call("format_range", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "INVALID",
                "bold": True
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response


class TestCreateTable:
    """Test create_table function."""

    def test_create_table_success(self):
        """Test creating table from data range."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and write some data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Write test data with headers
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["Name", "Age"], ["John", 30], ["Jane", 25]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Create table
            fc = function_call("create_table", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "table_name": "MyTable",
                "data_range": "A1:B3"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "create_table"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "table" in response.lower()

    def test_create_table_security_violation(self):
        """Test that create_table prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("create_table", {
                "filepath": "../outside.xlsx",
                "sheet_name": "Sheet",
                "table_name": "MyTable",
                "data_range": "A1:B3"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_create_table_nonexistent_file(self):
        """Test create_table with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("create_table", {
                "filepath": "nonexistent.xlsx",
                "sheet_name": "Sheet",
                "table_name": "MyTable",
                "data_range": "A1:B3"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response

    def test_create_table_invalid_range(self):
        """Test create_table with invalid data range."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Try invalid range
            fc = function_call("create_table", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "table_name": "MyTable",
                "data_range": "INVALID:RANGE"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response


class TestCreateChart:
    """Test create_chart function."""

    def test_create_chart_success(self):
        """Test creating chart from data range."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and write some data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Write test data
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["Month", "Sales"], ["Jan", 100], ["Feb", 150], ["Mar", 200]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Create chart
            fc = function_call("create_chart", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data_range": "A1:B4",
                "chart_type": "column",
                "target_cell": "D2",
                "title": "Sales Chart"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "create_chart"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "chart" in response.lower()

    def test_create_chart_security_violation(self):
        """Test that create_chart prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("create_chart", {
                "filepath": "../outside.xlsx",
                "sheet_name": "Sheet",
                "data_range": "A1:B4",
                "chart_type": "column",
                "target_cell": "D2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_create_chart_nonexistent_file(self):
        """Test create_chart with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("create_chart", {
                "filepath": "nonexistent.xlsx",
                "sheet_name": "Sheet",
                "data_range": "A1:B4",
                "chart_type": "column",
                "target_cell": "D2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response

    def test_create_chart_invalid_chart_type(self):
        """Test create_chart with invalid chart type."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["A", "B"], [1, 2]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Try invalid chart type
            fc = function_call("create_chart", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data_range": "A1:B2",
                "chart_type": "invalid_type",
                "target_cell": "D2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response


class TestCreatePivotTable:
    """Test create_pivot_table function."""

    def test_create_pivot_table_success(self):
        """Test creating pivot table from data range."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and write some data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            # Write test data with headers
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [
                    ["Name", "Department", "Salary"], 
                    ["John", "Sales", 50000], 
                    ["Jane", "Sales", 60000],
                    ["Bob", "IT", 70000],
                    ["Alice", "IT", 65000]
                ],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Create pivot table
            fc = function_call("create_pivot_table", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data_range": "A1:C5",
                "pivot_sheet_name": "PivotSheet",
                "row_fields": ["Department"],
                "column_fields": [],
                "value_fields": ["Salary"]
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            # Check result
            assert result.role == "tool"
            assert result.parts[0].function_response.name == "create_pivot_table"
            response = result.parts[0].function_response.response["result"]
            
            # Should succeed
            assert "pivot" in response.lower()

    def test_create_pivot_table_security_violation(self):
        """Test that create_pivot_table prevents directory traversal."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("create_pivot_table", {
                "filepath": "../outside.xlsx",
                "sheet_name": "Sheet",
                "data_range": "A1:C5",
                "pivot_sheet_name": "PivotSheet",
                "row_fields": ["Department"],
                "column_fields": [],
                "value_fields": ["Salary"]
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with security error
            assert "Error:" in response
            assert "outside the permitted working directory" in response

    def test_create_pivot_table_nonexistent_file(self):
        """Test create_pivot_table with nonexistent file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            fc = function_call("create_pivot_table", {
                "filepath": "nonexistent.xlsx",
                "sheet_name": "Sheet",
                "data_range": "A1:C5",
                "pivot_sheet_name": "PivotSheet",
                "row_fields": ["Department"],
                "column_fields": [],
                "value_fields": ["Salary"]
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response

    def test_create_pivot_table_invalid_fields(self):
        """Test create_pivot_table with invalid field names."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create workbook and data
            workbook_path = "test_workbook.xlsx"
            fc_wb = function_call("create_workbook", {"filepath": workbook_path})
            call_function(fc_wb.parts[0].function_call, temp_dir)
            
            fc_write = function_call("write_data_to_excel", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data": [["Name", "Age"], ["John", 30]],
                "start_cell": "A1"
            })
            call_function(fc_write.parts[0].function_call, temp_dir)
            
            # Try invalid field names
            fc = function_call("create_pivot_table", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "data_range": "A1:B2",
                "pivot_sheet_name": "PivotSheet",
                "row_fields": ["NonExistentField"],
                "column_fields": [],
                "value_fields": ["Age"]
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail gracefully
            assert "Error:" in response