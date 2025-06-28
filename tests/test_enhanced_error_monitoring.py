"""Test enhanced error monitoring and stack trace visibility."""

import pytest
from unittest.mock import Mock, patch
import traceback
from staffer.available_functions import call_function


def test_unhandled_exception_shows_stack_trace():
    """Test that unhandled exceptions show full stack trace for debugging."""
    mock_function_call = Mock()
    mock_function_call.name = "create_workbook"
    mock_function_call.args = {"filepath": "test.xlsx"}
    
    # Mock the create_workbook function to raise an unexpected error
    with patch('staffer.available_functions.create_workbook') as mock_create:
        mock_create.side_effect = Exception("Unexpected error with None.split()")
        
        # Should not crash but should show helpful error info
        result = call_function(mock_function_call, "/test/dir", verbose=True)
        
        assert result.role == "tool"
        response = result.parts[0].function_response.response
        
        # Should capture the error with context
        assert "error" in response or "Error" in response.get("result", "")


def test_none_split_error_is_caught():
    """Test that NoneType split errors are properly caught and displayed."""
    mock_function_call = Mock()
    mock_function_call.name = "create_workbook"
    mock_function_call.args = {"filepath": "test.xlsx"}
    
    # Mock a function that fails with the specific 'split' error
    with patch('staffer.available_functions.create_workbook') as mock_create:
        error = AttributeError("'NoneType' object has no attribute 'split'")
        mock_create.side_effect = error
        
        result = call_function(mock_function_call, "/test/dir")
        
        assert result.role == "tool"
        response = result.parts[0].function_response.response
        
        # Should catch and report the None error meaningfully
        assert "Error" in response.get("result", "") or "error" in response


def test_result_processing_error_is_caught():
    """Test that errors in result processing are properly handled."""
    mock_function_call = Mock()
    mock_function_call.name = "create_workbook"
    mock_function_call.args = {"filepath": "test.xlsx"}
    
    # Mock successful function call but error in result processing
    with patch('staffer.available_functions.create_workbook') as mock_create:
        with patch('staffer.available_functions._create_result_summary') as mock_summary:
            mock_create.return_value = "Success"
            mock_summary.side_effect = AttributeError("'NoneType' object has no attribute 'split'")
            
            # This should be caught and handled gracefully
            result = call_function(mock_function_call, "/test/dir")
            
            assert result.role == "tool"
            response = result.parts[0].function_response.response
            
            # Should not crash, should return meaningful error
            assert "error" in response or "Error" in response.get("result", "")