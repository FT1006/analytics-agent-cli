"""Test enhanced None error handling with improved visibility and recovery suggestions."""

import pytest
from unittest.mock import Mock
from staffer.available_functions import call_function


def test_enhanced_none_error_response_structure(temp_cwd):
    """Test that enhanced None error responses have proper structure."""
    
    mock_function_call = Mock()
    mock_function_call.name = 'get_file_content'
    mock_function_call.args = {'file_path': None}
    
    result = call_function(mock_function_call, str(temp_cwd))
    
    # Verify response structure
    assert result.role == "tool"
    response = result.parts[0].function_response.response
    
    # Should have user-friendly message
    assert "result" in response
    assert "❌ None Value Error" in response["result"]
    assert "None parameters: file_path" in response["result"]
    assert "💡 Try:" in response["result"]
    
    # Should have detailed error context for debugging
    assert "error_details" in response
    error_details = response["error_details"]
    
    assert error_details["error_type"] == "None Value Error (TypeError)"
    assert error_details["function"] == "get_file_content"
    assert "context" in error_details
    assert "suggestions" in error_details
    assert error_details["context"]["none_parameters"] == ["file_path"]


def test_function_specific_recovery_suggestions(temp_cwd):
    """Test that recovery suggestions are function-specific and helpful."""
    
    # Test create_worksheet with None parameters
    mock_function_call = Mock()
    mock_function_call.name = 'create_worksheet'
    mock_function_call.args = {'filepath': None, 'sheet_name': None}
    
    result = call_function(mock_function_call, str(temp_cwd))
    response = result.parts[0].function_response.response
    
    # Should have function-specific suggestions
    error_details = response["error_details"]
    suggestions = error_details["suggestions"]
    
    # Should suggest providing the None parameters
    assert any("Provide values for:" in s for s in suggestions)
    # Should have specific suggestion for worksheet functions
    assert any("filepath and sheet_name" in s for s in suggestions)


def test_error_context_tracking(temp_cwd):
    """Test that error context properly tracks parameter issues."""
    
    mock_function_call = Mock()
    mock_function_call.name = 'write_file'
    mock_function_call.args = {
        'file_path': None,
        'content': ''  # Empty string
    }
    
    result = call_function(mock_function_call, str(temp_cwd))
    response = result.parts[0].function_response.response
    
    error_details = response["error_details"]
    context = error_details["context"]
    
    # Should properly track different parameter issues
    assert context["args_provided"] == ['file_path', 'content']
    assert context["none_parameters"] == ['file_path']
    assert context["empty_parameters"] == ['content']


def test_enhanced_error_backward_compatibility(temp_cwd):
    """Test that enhanced errors don't break existing error handling."""
    
    # Test with a function that doesn't exist
    mock_function_call = Mock()
    mock_function_call.name = 'nonexistent_function'
    mock_function_call.args = {}
    
    result = call_function(mock_function_call, str(temp_cwd))
    response = result.parts[0].function_response.response
    
    # Should still handle unknown functions properly
    assert "error" in response
    assert "Unknown function" in response["error"]


def test_non_none_related_errors_passthrough(temp_cwd):
    """Test that non-None errors are properly re-raised."""
    
    # Create a mock that works normally 
    mock_function_call = Mock()
    mock_function_call.name = 'get_files_info'  # Valid function
    mock_function_call.args = {}  # No args needed for get_files_info
    
    # This should work normally (no enhanced error handling triggered)
    result = call_function(mock_function_call, str(temp_cwd))
    
    # Should get normal function response, not enhanced error
    response = result.parts[0].function_response.response
    assert "result" in response
    # Should not have enhanced error structure
    assert "error_details" not in response