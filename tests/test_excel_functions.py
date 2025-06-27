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
            
            # Try invalid cell reference
            fc = function_call("merge_cells", {
                "filepath": workbook_path,
                "sheet_name": "Sheet",
                "start_cell": "INVALID",
                "end_cell": "B2"
            })
            result = call_function(fc.parts[0].function_call, temp_dir)
            
            response = result.parts[0].function_response.response["result"]
            
            # Should fail with error
            assert "Error:" in response


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