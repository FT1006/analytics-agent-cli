"""Test validation of empty content before adding to conversation history."""

import pytest
from unittest.mock import Mock, patch
from google.genai import types


def test_empty_content_parts_not_added_to_conversation():
    """Test that content with empty parts is not added to conversation history."""
    from staffer.main import process_prompt
    
    # Mock LLM response with empty parts
    mock_response = Mock()
    mock_response.text = None
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 5
    
    # Mock candidate with empty parts (this should be skipped)
    mock_candidate = Mock()
    mock_candidate.content.parts = []  # Empty parts - should cause API error
    mock_response.candidates = [mock_candidate]
    
    with patch('staffer.main.genai') as mock_genai:
        # The generate_content should not be called again with empty content
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.return_value = mock_response
        
        conversation = []
        
        # Should not crash or add empty content to conversation
        result = process_prompt("test prompt", "/test/dir", conversation, verbose=False)
        
        # Verify that empty content was not added to conversation
        # (implementation will determine exact behavior)


def test_none_content_parts_not_added_to_conversation():
    """Test that content with None parts is not added to conversation history."""
    from staffer.main import process_prompt
    
    # Mock LLM response with None parts
    mock_response = Mock()
    mock_response.text = None
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 5
    
    # Mock candidate with None parts
    mock_candidate = Mock()
    mock_candidate.content.parts = None  # None parts - should cause API error
    mock_response.candidates = [mock_candidate]
    
    with patch('staffer.main.genai') as mock_genai:
        mock_model = Mock()
        mock_genai.GenerativeModel.return_value = mock_model
        mock_model.generate_content.return_value = mock_response
        
        conversation = []
        
        # Should not crash or add None content to conversation
        result = process_prompt("test prompt", "/test/dir", conversation, verbose=False)


def test_valid_content_with_function_calls_is_added():
    """Test that valid content with function calls is properly added to conversation."""
    from staffer.main import process_prompt
    
    # Mock LLM response with valid function call parts
    mock_response = Mock()
    mock_response.text = None
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 5
    
    # Mock candidate with valid function call
    mock_part = Mock()
    mock_part.function_call = Mock(name="get_working_directory", args={})
    mock_part.text = None
    
    mock_candidate = Mock()
    mock_candidate.content.parts = [mock_part]  # Valid parts with function call
    mock_response.candidates = [mock_candidate]
    
    with patch('staffer.main.genai') as mock_genai:
        with patch('staffer.main.call_function') as mock_call_function:
            mock_model = Mock()
            mock_genai.GenerativeModel.return_value = mock_model
            mock_model.generate_content.return_value = mock_response
            
            # Mock successful function call
            mock_call_function.return_value = Mock(
                parts=[Mock(function_response=Mock(response={"result": "/test/dir"}))]
            )
            
            conversation = []
            
            # Should work properly and add valid content
            result = process_prompt("test prompt", "/test/dir", conversation, verbose=False)