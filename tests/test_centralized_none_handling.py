"""Test centralized None handling in call_function."""

import pytest
from unittest.mock import Mock, patch
from google.genai import types
from staffer.available_functions import call_function


def test_call_function_catches_none_attribute_errors():
    """Test that call_function catches AttributeError from None values."""
    
    # Create a mock function call that will trigger AttributeError
    mock_function_call = Mock()
    mock_function_call.name = "read_data_from_excel"
    mock_function_call.args = {
        "filepath": "test.xlsx",
        "sheet_name": "Sheet1", 
        "start_cell": None,  # This would cause the bug
        "end_cell": None
    }
    
    # Mock the function to raise AttributeError like the real bug
    with patch('staffer.functions.read_data_from_excel.read_data_from_excel') as mock_read:
        mock_read.side_effect = AttributeError("'NoneType' object has no attribute 'split'")
        
        # Call the function through call_function
        result = call_function(mock_function_call, "/test/dir")
        
        # Should return an error response, not crash
        assert result.role == "tool"
        response = result.parts[0].function_response.response
        assert "Error" in response["result"]
        assert "NoneType" in response["result"]


def test_call_function_preserves_non_none_values():
    """Test that call_function preserves non-None values."""
    
    mock_function_call = Mock()
    mock_function_call.name = "write_data_to_excel"
    mock_function_call.args = {
        "filepath": "test.xlsx",
        "sheet_name": "Sheet1",
        "start_cell": "B2",  # Non-None value
        "data": [["value1", "value2"]]
    }
    
    with patch('staffer.functions.write_data_to_excel.write_data_to_excel') as mock_write:
        mock_write.return_value = "Success"
        
        result = call_function(mock_function_call, "/test/dir")
        
        # All non-None values should be passed through
        call_args = mock_write.call_args[1]
        assert call_args["filepath"] == "test.xlsx"
        assert call_args["sheet_name"] == "Sheet1"
        assert call_args["start_cell"] == "B2"
        assert call_args["data"] == [["value1", "value2"]]


def test_real_scenario_with_none_handling():
    """Test that the None handling prevents the actual bug."""
    
    # This simulates what the LLM might pass
    mock_function_call = Mock()
    mock_function_call.name = "read_data_from_excel"
    mock_function_call.args = {
        "filepath": "supermarket_sales.xlsx",
        "sheet_name": None,  # LLM might pass None
        "start_cell": None   # LLM might pass None
    }
    
    # This should not crash with AttributeError
    result = call_function(mock_function_call, "/test/dir")
    
    # Should get a proper error message, not a crash
    assert result.role == "tool"
    response = result.parts[0].function_response.response
    assert "Error" in response["result"] or "error" in response


def test_call_function_catches_type_errors():
    """Test that call_function catches TypeError from None values."""
    
    # Create a mock function call that will trigger TypeError
    mock_function_call = Mock()
    mock_function_call.name = "create_chart"
    mock_function_call.args = {
        "filepath": "test.xlsx",
        "sheet_name": "Sheet1",
        "chart_type": "column",
        "data_range": None,  # This could cause TypeError: 'NoneType' object is not iterable
        "target_cell": "E1"
    }
    
    # Mock the function to raise TypeError
    with patch('staffer.functions.create_chart.create_chart') as mock_create:
        mock_create.side_effect = TypeError("argument of type 'NoneType' is not iterable")
        
        # Call the function through call_function
        result = call_function(mock_function_call, "/test/dir")
        
        # Should return an error response, not crash
        assert result.role == "tool"
        response = result.parts[0].function_response.response
        assert "Error" in response["result"]
        assert "NoneType" in response["result"]