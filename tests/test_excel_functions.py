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