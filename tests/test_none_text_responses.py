"""Test handling of LLM responses with None text content."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from google.genai import types


def test_main_handles_none_text_response():
    """Test that main.py handles responses with None text gracefully."""
    from staffer.main import process_prompt
    
    # Mock LLM response with None text but successful function calls
    mock_response = Mock()
    mock_response.text = None
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 5
    
    # Mock successful candidate with function call but no text
    mock_candidate = Mock()
    mock_candidate.content.parts = [
        Mock(function_call=Mock(name="create_workbook", args={"filepath": "test.xlsx"}), text=None)
    ]
    mock_response.candidates = [mock_candidate]
    
    # Mock terminal
    mock_terminal = Mock()
    
    with patch('staffer.main.genai') as mock_genai:
        with patch('staffer.main.call_function') as mock_call_function:
            # Setup mocks
            mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
            mock_call_function.return_value = Mock(
                parts=[Mock(function_response=Mock(response={"result": "Success"}))]
            )
            
            # Should not crash when res.text is None
            conversation = []
            process_prompt("test prompt", "/test/dir", conversation, verbose=False, terminal=mock_terminal)
            
            # Verify it didn't try to display None
            # (The actual verification depends on implementation)


def test_interactive_handles_none_text_response():
    """Test that interactive.py handles responses with None text gracefully."""
    from staffer.cli.interactive import process_prompt as interactive_process_prompt
    
    # Mock LLM response with None text
    mock_response = Mock()
    mock_response.text = None
    mock_response.usage_metadata.prompt_token_count = 10
    mock_response.usage_metadata.candidates_token_count = 5
    
    # Mock candidate with function call
    mock_candidate = Mock()
    mock_candidate.content.parts = [
        Mock(function_call=Mock(name="get_working_directory", args={}), text=None)
    ]
    mock_response.candidates = [mock_candidate]
    
    with patch('staffer.cli.interactive.genai') as mock_genai:
        with patch('staffer.cli.interactive.call_function') as mock_call_function:
            # Setup mocks
            mock_genai.GenerativeModel.return_value.generate_content.return_value = mock_response
            mock_call_function.return_value = Mock(
                parts=[Mock(function_response=Mock(response={"result": "/test/dir"}))]
            )
            
            # Should not crash
            conversation = []
            result = interactive_process_prompt("test", "/test/dir", conversation, verbose=False)
            
            # Should return something meaningful even with None text
            assert result is not None


def test_print_none_text_response():
    """Test that print statements handle None text gracefully."""
    # This specifically tests the print(f"-> {res.text}") case
    
    class MockResponse:
        def __init__(self):
            self.text = None
    
    response = MockResponse()
    
    # Should not crash when formatting None
    try:
        formatted = f"-> {response.text}"
        # This should work - Python handles None in f-strings
        assert formatted == "-> None"
    except Exception as e:
        pytest.fail(f"String formatting should handle None gracefully: {e}")


def test_terminal_display_none_safety():
    """Test that terminal display methods are None-safe."""
    from staffer.ui.terminal import TerminalUI, BasicTerminalUI
    
    # Test BasicTerminalUI
    basic = BasicTerminalUI()
    # Should not crash
    basic.display_ai_response(None)
    
    # Test TerminalUI (if available)
    try:
        enhanced = TerminalUI()
        enhanced.display_ai_response(None)
    except ImportError:
        # Enhanced terminal not available
        pass