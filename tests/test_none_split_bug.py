"""Test that None values are handled properly through centralized error handling."""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path


def test_none_values_handled_centrally():
    """Test that None values are now handled by the centralized error handler."""
    # The centralized handler in call_function now catches all None-related errors
    # Individual functions no longer need explicit None checks
    # This demonstrates the improved approach
    from staffer.available_functions import call_function
    
    # Test case that would previously crash
    mock_function_call = Mock()
    mock_function_call.name = "read_data_from_excel"
    mock_function_call.args = {
        "filepath": "test.xlsx",
        "sheet_name": None,  # This would cause the original bug
        "start_cell": None   # This too
    }
    
    # Should return error response, not crash
    result = call_function(mock_function_call, "/test/dir")
    
    assert result.role == "tool"
    response = result.parts[0].function_response.response
    # Should get meaningful error, not crash
    assert "Error" in response.get("result", "") or "error" in response


def test_format_validation_still_works():
    """Test that meaningful validation (format checks) still work."""
    from staffer.functions.create_chart import create_chart
    
    # Format validation should still catch invalid ranges
    result = create_chart("/tmp", "test.xlsx", "Sheet1", "Column", "A1", "E1")  # Missing ':'
    assert "Error" in result
    assert "format" in result.lower()


def test_business_logic_validation_preserved():
    """Test that business logic validation is preserved."""
    from staffer.functions.create_pivot_table import create_pivot_table
    
    # Format validation should still work
    result = create_pivot_table(
        "/tmp", "test.xlsx", "Sheet1", 
        "A1",  # Invalid format - missing ':'
        "Pivot",
        ["Product"],
        [],
        ["Sales"]
    )
    assert "Error" in result
    assert "format" in result.lower()