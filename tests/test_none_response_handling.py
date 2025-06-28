"""Test handling of None responses after function calls."""

import pytest
from unittest.mock import Mock, patch
from staffer.ui.terminal import TerminalUI, BasicTerminalUI


def test_terminal_ui_handles_none_response():
    """Test that TerminalUI handles None response gracefully."""
    try:
        terminal = TerminalUI()
    except ImportError:
        pytest.skip("Enhanced terminal features not available")
    
    # Should not crash when response is None
    terminal.display_ai_response(None)


def test_basic_terminal_ui_handles_none_response():
    """Test that BasicTerminalUI handles None response gracefully.""" 
    terminal = BasicTerminalUI()
    
    # Should not crash when response is None
    terminal.display_ai_response(None)


def test_terminal_ui_handles_empty_response():
    """Test that TerminalUI handles empty string response."""
    try:
        terminal = TerminalUI()
    except ImportError:
        pytest.skip("Enhanced terminal features not available")
    
    # Should handle empty string gracefully
    terminal.display_ai_response("")
    terminal.display_ai_response("   ")  # whitespace only


def test_basic_terminal_ui_handles_empty_response():
    """Test that BasicTerminalUI handles empty string response."""
    terminal = BasicTerminalUI()
    
    # Should handle empty string gracefully  
    terminal.display_ai_response("")
    terminal.display_ai_response("   ")  # whitespace only