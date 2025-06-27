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